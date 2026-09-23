"""Request core shared by the sync and async clients."""

from __future__ import annotations

import asyncio
import json
import platform
import random
import time
import uuid
from collections.abc import Awaitable, Mapping
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Optional, Union
from urllib.parse import quote

import httpx
from pydantic import BaseModel
from typing_extensions import TypedDict

from ._errors import (
    APIConnectionError,
    APITimeoutError,
    ConfigurationError,
    InvalidRequestError,
    VexPayError,
    error_from_response,
)
from ._version import __version__

DEFAULT_BASE_URL = "https://api.pay.vexwallet.co"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_NETWORK_RETRIES = 2

_INITIAL_RETRY_DELAY = 0.5
_MAX_RETRY_DELAY = 8.0
_MAX_RETRY_AFTER = 60.0

QueryValue = Union[str, int, float, bool, None]
Body = Union[Mapping[str, Any], BaseModel, list[Any], None]


class RequestOptions(TypedDict, total=False):
    """Per-call options accepted by every resource method."""

    #: Sent as ``Idempotency-Key`` on POST. Defaults to a random UUID per call, reused across retries.
    idempotency_key: str
    #: Overrides the client's timeout (seconds) for this call.
    timeout: float
    #: Overrides the client's ``max_network_retries`` for this call.
    max_network_retries: int


def user_agent() -> str:
    return f"vexpay-python/{__version__} python/{platform.python_version()}"


def parse_retry_after(value: Optional[str], now: Optional[float] = None) -> Optional[float]:
    """``Retry-After`` as seconds or an HTTP date → seconds, capped at 60."""
    if not value:
        return None
    try:
        seconds = float(value)
        if seconds >= 0:
            return min(seconds, _MAX_RETRY_AFTER)
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(value).timestamp()
    except (TypeError, ValueError, IndexError):
        return None
    current = time.time() if now is None else now
    return min(max(0.0, when - current), _MAX_RETRY_AFTER)


def backoff_delay(attempt: int, rand: Callable[[], float] = random.random) -> float:
    """Exponential backoff with jitter: attempt 0 → [0.25, 0.5) s, doubling, capped at 8 s."""
    ceiling = min(_INITIAL_RETRY_DELAY * 2.0**attempt, _MAX_RETRY_DELAY)
    return ceiling / 2 + rand() * (ceiling / 2)


def is_retryable(error: VexPayError) -> bool:
    if isinstance(error, APIConnectionError):
        return True
    if error.status == 429:
        return True
    if error.status is not None and error.status >= 500:
        return True
    return error.status == 409 and error.code == "idempotency_request_in_progress"


def serialize_body(body: Body) -> Optional[bytes]:
    if body is None:
        return None
    if isinstance(body, BaseModel):
        # Only fields the caller set — server-side defaults stay server-side.
        payload: Any = body.model_dump(mode="json", by_alias=True, exclude_unset=True)
    elif isinstance(body, Mapping):
        payload = {
            key: (value.model_dump(mode="json", by_alias=True, exclude_unset=True) if isinstance(value, BaseModel) else value)
            for key, value in body.items()
        }
    else:
        payload = body
    return json.dumps(payload, separators=(",", ":"), default=str).encode("utf-8")


def fill_path(template: str, params: Mapping[str, str]) -> str:
    def replace(name: str) -> str:
        value = params.get(name)
        if not isinstance(value, str) or value == "":
            raise InvalidRequestError(f'Missing required path parameter "{name}".')
        return quote(value, safe="")

    out = ""
    rest = template
    while "{" in rest:
        before, _, after = rest.partition("{")
        name, _, rest = after.partition("}")
        out += before + replace(name)
    return out + rest


def _parse_content(content: bytes) -> Any:
    if not content:
        return None
    try:
        return json.loads(content)
    except ValueError:
        return content.decode("utf-8", errors="replace")


@dataclass
class PreparedRequest:
    method: str
    url: str
    params: dict[str, str]
    headers: dict[str, str]
    content: Optional[bytes]


class _Config:
    def __init__(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        timeout: Optional[float],
        max_network_retries: Optional[int],
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ConfigurationError(
                "A VEXPay API key is required: VexPay(api_key=os.environ['VEXPAY_API_KEY'])."
            )
        self.api_key = api_key.strip()
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = DEFAULT_TIMEOUT if timeout is None else timeout
        self.max_network_retries = (
            DEFAULT_MAX_NETWORK_RETRIES if max_network_retries is None else max_network_retries
        )

    def prepare(
        self,
        method: str,
        path: str,
        *,
        query: Optional[Mapping[str, QueryValue]] = None,
        body: Body = None,
        idempotency_key: Optional[str] = None,
    ) -> PreparedRequest:
        headers = {
            "accept": "application/json",
            "x-api-key": self.api_key,
            "user-agent": user_agent(),
        }
        content = serialize_body(body)
        if content is not None:
            headers["content-type"] = "application/json"
        # One key for every attempt of this call: a retried POST can never charge twice.
        if method == "POST":
            headers["idempotency-key"] = idempotency_key or str(uuid.uuid4())
        params = {
            key: ("true" if value is True else "false" if value is False else str(value))
            for key, value in (query or {}).items()
            if value is not None
        }
        return PreparedRequest(method, f"{self.base_url}{path}", params, headers, content)


def _result(response: httpx.Response) -> tuple[Any, Optional[VexPayError], Optional[float]]:
    body = _parse_content(response.content)
    if response.is_success:
        return body, None, None
    error = error_from_response(response.status_code, body, response.headers.get("x-request-id"))
    return None, error, parse_retry_after(response.headers.get("retry-after"))


def _transport_error(exc: httpx.HTTPError, timeout: float) -> VexPayError:
    if isinstance(exc, httpx.TimeoutException):
        return APITimeoutError(f"Request to VEXPay timed out after {timeout}s")
    return APIConnectionError(f"Could not reach VEXPay: {exc}")


class SyncHttp:
    def __init__(
        self,
        config: _Config,
        client: Optional[httpx.Client] = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self._client = client or httpx.Client()
        self._owns_client = client is None
        self._sleep = sleep

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Optional[Mapping[str, QueryValue]] = None,
        body: Body = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        opts = options or {}
        timeout = opts.get("timeout", self.config.timeout)
        max_retries = opts.get("max_network_retries", self.config.max_network_retries)
        req = self.config.prepare(
            method, path, query=query, body=body, idempotency_key=opts.get("idempotency_key")
        )
        attempt = 0
        while True:
            retry_after: Optional[float] = None
            try:
                response = self._client.request(
                    req.method, req.url, params=req.params, headers=req.headers, content=req.content, timeout=timeout
                )
                result, error, retry_after = _result(response)
                if error is None:
                    return result
            except httpx.HTTPError as exc:
                error = _transport_error(exc, timeout)
            if attempt >= max_retries or not is_retryable(error):
                raise error
            self._sleep(retry_after if retry_after is not None else backoff_delay(attempt))
            attempt += 1

    def close(self) -> None:
        if self._owns_client:
            self._client.close()


class AsyncHttp:
    def __init__(
        self,
        config: _Config,
        client: Optional[httpx.AsyncClient] = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self.config = config
        self._client = client or httpx.AsyncClient()
        self._owns_client = client is None
        self._sleep = sleep

    async def request(
        self,
        method: str,
        path: str,
        *,
        query: Optional[Mapping[str, QueryValue]] = None,
        body: Body = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        opts = options or {}
        timeout = opts.get("timeout", self.config.timeout)
        max_retries = opts.get("max_network_retries", self.config.max_network_retries)
        req = self.config.prepare(
            method, path, query=query, body=body, idempotency_key=opts.get("idempotency_key")
        )
        attempt = 0
        while True:
            retry_after: Optional[float] = None
            try:
                response = await self._client.request(
                    req.method, req.url, params=req.params, headers=req.headers, content=req.content, timeout=timeout
                )
                result, error, retry_after = _result(response)
                if error is None:
                    return result
            except httpx.HTTPError as exc:
                error = _transport_error(exc, timeout)
            if attempt >= max_retries or not is_retryable(error):
                raise error
            await self._sleep(retry_after if retry_after is not None else backoff_delay(attempt))
            attempt += 1

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()
