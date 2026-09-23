"""Official Python SDK for the VEXPay API."""

from ._client import AsyncVexPay, VexPay
from ._core import DEFAULT_BASE_URL, RequestOptions
from ._pagination import AsyncPage, SyncPage
from ._errors import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    ConfigurationError,
    ConflictError,
    InvalidRequestError,
    NotFoundError,
    RateLimitError,
    SignatureVerificationError,
    VexPayError,
)
from ._version import __version__
from ._webhooks import (
    DEFAULT_TOLERANCE,
    SIGNATURE_HEADER,
    WEBHOOK_EVENT_NAMES,
    GenericEvent,
    PaymentEvent,
    PaymentWebhookData,
    Webhook,
    WebhookEvent,
)

__all__ = [
    "DEFAULT_TOLERANCE",
    "GenericEvent",
    "PaymentEvent",
    "PaymentWebhookData",
    "SIGNATURE_HEADER",
    "WEBHOOK_EVENT_NAMES",
    "Webhook",
    "WebhookEvent",
    "APIConnectionError",
    "APIError",
    "APITimeoutError",
    "AsyncPage",
    "AsyncVexPay",
    "AuthenticationError",
    "ConfigurationError",
    "ConflictError",
    "DEFAULT_BASE_URL",
    "InvalidRequestError",
    "NotFoundError",
    "RateLimitError",
    "RequestOptions",
    "SignatureVerificationError",
    "SyncPage",
    "VexPay",
    "VexPayError",
    "__version__",
]
