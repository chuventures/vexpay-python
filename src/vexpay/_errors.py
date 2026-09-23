from __future__ import annotations

import re
from typing import Any, Optional


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
    ) -> None:
        super().__init__(message)
        self.message = message
        #: HTTP status, when the API answered.
        self.status = status
        #: Machine-readable API code, e.g. ``insufficient_balance``.
        self.code = code
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
    """429 — too many requests. Retried automatically before surfacing."""


class APIError(VexPayError):
    """5xx — VEXPay or an upstream bank failed. Retried automatically before surfacing."""


class APIConnectionError(VexPayError):
    """The request never got an HTTP answer (DNS, refused, reset)."""


class APITimeoutError(APIConnectionError):
    """The request exceeded its timeout."""


class SignatureVerificationError(VexPayError):
    """A webhook signature did not verify (see ``Webhook.construct_event``)."""


_MACHINE_CODE = re.compile(r"^[a-z][a-z0-9_]*$")


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
    return f"VEXPay API responded with HTTP {status}"


def error_from_response(status: int, body: Any, request_id: Optional[str] = None) -> VexPayError:
    """Maps an HTTP error response to the matching error class."""
    raw_code = body.get("error") if isinstance(body, dict) else None
    code = raw_code if isinstance(raw_code, str) and _MACHINE_CODE.match(raw_code) else None
    message = _message_from(body, status)
    kwargs: dict[str, Any] = {"status": status, "code": code, "body": body, "request_id": request_id}

    if status == 401:
        return AuthenticationError(message, **kwargs)
    if status == 404:
        return NotFoundError(message, **kwargs)
    if status == 409:
        return ConflictError(message, **kwargs)
    if status == 429:
        return RateLimitError(message, **kwargs)
    if status >= 500:
        return APIError(message, **kwargs)
    return InvalidRequestError(message, **kwargs)
