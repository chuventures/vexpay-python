from __future__ import annotations

import re
from typing import Any, Mapping, Optional


class VexPayError(Exception):
    """Base class for every error the SDK raises."""

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        code: Optional[str] = None,
        body: Any = None,
        request_id: Optional[str] = None,
        doc_url: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        #: HTTP status, when the API answered.
        self.status = status
        #: Stable API code: the body's ``code`` (e.g. ``insufficient_balance``, ``validation_failed``, or an
        #: uppercase risk or bank code such as ``CARD_VELOCITY_BLOCKED``), else a lowercase ``error``.
        self.code = code
        #: Docs page for ``code``, e.g. ``https://docs.vexpay.app/errors#insufficient_balance``, when sent.
        self.doc_url = doc_url
        #: Parsed response body, when the API answered.
        self.body = body
        #: Value of the ``x-request-id`` response header, when present.
        self.request_id = request_id

    def __repr__(self) -> str:
        return f"{type(self).__name__}(message={self.message!r}, status={self.status!r}, code={self.code!r})"


class ConfigurationError(VexPayError):
    """Invalid client configuration (e.g. a missing API key). Raised before any request."""


class AuthenticationError(VexPayError):
    """401 — missing, invalid, or revoked API key."""


class InvalidRequestError(VexPayError):
    """400, 403, 410, 422 and other non-retryable 4xx — fix the request before retrying."""


class NotFoundError(VexPayError):
    """404 — the resource does not exist (or belongs to another account)."""


class ConflictError(VexPayError):
    """409 — e.g. ``external_ref_conflict``, ``idempotency_key_reused``."""


class RateLimitError(VexPayError):
    """429.

    When ``is_rate_limit`` is true (VEX Pay's rate limiter: body ``error`` = ``rate_limited`` or a
    ``RateLimit`` header), it was retried after ``Retry-After`` before surfacing. Otherwise it is a
    risk decline (e.g. ``CARD_VELOCITY_BLOCKED``) and was not retried.
    """

    def __init__(
        self,
        message: str,
        *,
        is_rate_limit: bool = False,
        retry_after_seconds: Optional[float] = None,
        rate_limit: Optional[str] = None,
        rate_limit_policy: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        #: True when the API's rate limiter refused the request.
        self.is_rate_limit = is_rate_limit
        #: Seconds to wait, from the ``Retry-After`` header, when present.
        self.retry_after_seconds = retry_after_seconds
        #: Raw ``RateLimit`` header, e.g. ``"write";r=0;t=2``.
        self.rate_limit = rate_limit
        #: Raw ``RateLimit-Policy`` header, e.g. ``"write";q=50;w=2``.
        self.rate_limit_policy = rate_limit_policy


class APIError(VexPayError):
    """5xx — VEX Pay or an upstream bank failed. Retried automatically before surfacing."""


class APIConnectionError(VexPayError):
    """The request never got an HTTP answer (DNS, refused, reset)."""


class APITimeoutError(APIConnectionError):
    """The request exceeded its timeout."""


class SignatureVerificationError(VexPayError):
    """A webhook signature did not verify (see ``Webhook.construct_event``)."""


# Legacy ``error`` values that are codes (not HTTP reason phrases such as ``Bad Request``).
_MACHINE_CODE = re.compile(r"^[a-z][a-z0-9_]*$")
# ``code`` is stable: lowercase snake_case, or an uppercase risk or bank code (``PAYER_BLOCKED``, ``AM04``).
_API_CODE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_]*$")


def _code_from(body: Any) -> Optional[str]:
    """The body's ``code`` first, then a machine-readable ``error`` (APIs before ``code`` existed)."""
    if not isinstance(body, dict):
        return None
    code = body.get("code")
    if isinstance(code, str) and _API_CODE.match(code):
        return code
    error = body.get("error")
    if isinstance(error, str) and _MACHINE_CODE.match(error):
        return error
    return None


def _doc_url_from(body: Any) -> Optional[str]:
    doc_url = body.get("docUrl") if isinstance(body, dict) else None
    return doc_url if isinstance(doc_url, str) and doc_url else None


def _message_from(body: Any, status: int) -> str:
    if isinstance(body, dict):
        message = body.get("message")
        if isinstance(message, list):
            return "; ".join(str(m) for m in message)
        if isinstance(message, str) and message:
            return message
        error = body.get("error")
        if isinstance(error, str) and error:
            return error
    if isinstance(body, str) and body:
        return body
    return f"VEX Pay API responded with HTTP {status}"


def error_from_response(
    status: int,
    body: Any,
    request_id: Optional[str] = None,
    headers: Optional[Mapping[str, str]] = None,
) -> VexPayError:
    """Maps an HTTP error response to the matching error class."""
    code = _code_from(body)
    message = _message_from(body, status)
    kwargs: dict[str, Any] = {
        "status": status,
        "code": code,
        "body": body,
        "request_id": request_id,
        "doc_url": _doc_url_from(body),
    }

    if status == 401:
        return AuthenticationError(message, **kwargs)
    if status == 404:
        return NotFoundError(message, **kwargs)
    if status == 409:
        return ConflictError(message, **kwargs)
    if status == 429:
        rate_limit = headers.get("ratelimit") if headers is not None else None
        retry_after: Optional[float] = None
        try:
            raw = headers.get("retry-after") if headers is not None else None
            retry_after = float(raw) if raw is not None and float(raw) >= 0 else None
        except ValueError:
            retry_after = None
        return RateLimitError(
            message,
            is_rate_limit=bool(rate_limit)
            or code == "rate_limited"
            or (isinstance(body, dict) and body.get("error") == "rate_limited"),
            retry_after_seconds=retry_after,
            rate_limit=rate_limit,
            rate_limit_policy=headers.get("ratelimit-policy") if headers is not None else None,
            **kwargs,
        )
    if status >= 500:
        return APIError(message, **kwargs)
    return InvalidRequestError(message, **kwargs)
