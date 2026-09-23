"""Verify VEXPay webhook deliveries (``VexPay-Signature: t=<unix>,v1=<hex hmac>``)."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, ValidationError

from ._errors import SignatureVerificationError

WEBHOOK_EVENT_NAMES: tuple[str, ...] = (
    "payment.pending",
    "payment.completed",
    "payment.failed",
    "payment.canceled",
    "payment.reversed",
    "merchant.verified",
    "merchant.rejected",
    "merchant.deactivated",
    "merchant.reactivated",
    "merchant.balance.updated",
    "merchant.created",
    "merchant.activated",
    "merchant.updated",
    "merchant.kyb_required",
    "merchant.restricted",
    "merchant.capability.updated",
    "merchant.wallet_credit",
    "payout.completed",
    "payout.failed",
    "tenant.status_changed",
    "tenant.api_key.created",
    "tenant.api_key.rotated",
    "tenant.api_key.revoked",
    "notification.test",
)

SIGNATURE_HEADER = "VexPay-Signature"
DEFAULT_TOLERANCE = 300

_RAW_BODY_HINT = (
    "Pass the raw request body exactly as received (str or bytes). Parsing and re-serializing JSON — "
    "e.g. json.dumps(request.json) — changes the bytes and breaks the signature. In Flask use "
    "request.get_data(); in Django request.body; in FastAPI await request.body()."
)


class CheckoutSessionRef(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    reference: Optional[str] = None
    metadata: dict[str, str] = {}


class PaymentWebhookData(BaseModel):
    """``data`` of every ``payment.*`` event. Lenient on purpose: a verified delivery never fails to parse."""

    model_config = ConfigDict(extra="allow")

    paymentId: str
    externalRef: Optional[str] = None
    status: Literal["PENDING", "COMPLETED", "FAILED", "CANCELED", "REVERSED"]
    method: Optional[str] = None
    usdAmount: Optional[float] = None
    vesAmount: Optional[float] = None
    bcvRate: Optional[float] = None
    feeUsd: Optional[float] = None
    feeVes: Optional[float] = None
    netVes: Optional[float] = None
    bankReference: Optional[str] = None
    bankTxId: Optional[int] = None
    debtorId: Optional[str] = None
    debtorPhone: Optional[str] = None
    debtorBankCode: Optional[int] = None
    debtorBankName: Optional[str] = None
    cardLast4: Optional[str] = None
    cardBrand: Optional[str] = None
    tenantName: Optional[str] = None
    createdAt: Optional[str] = None
    failureCode: Optional[str] = None
    cancelReason: Optional[str] = None
    livemode: Optional[bool] = None
    #: Present when the payment came from a checkout session.
    checkoutSession: Optional[CheckoutSessionRef] = None


class PaymentEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event: str
    data: PaymentWebhookData
    timestamp: str


class GenericEvent(BaseModel):
    """Any non-payment event (and events newer than this SDK)."""

    model_config = ConfigDict(extra="allow")

    event: str
    data: dict[str, Any]
    timestamp: str


WebhookEvent = Union[PaymentEvent, GenericEvent]


def _sign(secret: str, timestamp: int, payload: str) -> str:
    return hmac.new(secret.encode(), f"{timestamp}.{payload}".encode(), hashlib.sha256).hexdigest()


def _parse_header(header: str) -> Optional[tuple[int, list[str]]]:
    timestamp: Optional[str] = None
    signatures: list[str] = []
    for part in header.split(","):
        key, sep, value = part.partition("=")
        key, value = key.strip(), value.strip()
        if not sep or not key:
            return None
        if key == "t":
            timestamp = value
        elif key == "v1":
            signatures.append(value)
        # Unknown schemes (v0, future v2…) are ignored.
    if not timestamp or not timestamp.isdigit():
        return None
    return int(timestamp), signatures


class Webhook:
    """Offline helpers — no API calls."""

    @staticmethod
    def construct_event(
        payload: Union[str, bytes],
        sig_header: Optional[str],
        secret: str,
        tolerance: int = DEFAULT_TOLERANCE,
        *,
        now: Optional[int] = None,
    ) -> WebhookEvent:
        """Verify a delivery and return the parsed event.

        Raises :class:`SignatureVerificationError` on a bad signature or a timestamp
        outside ``tolerance`` seconds (possible replay).
        """
        if isinstance(payload, (bytes, bytearray)):
            body = bytes(payload).decode("utf-8")
        elif isinstance(payload, str):
            body = payload
        else:
            raise SignatureVerificationError(f"Webhook payload must be the raw body. {_RAW_BODY_HINT}")
        if not secret:
            raise SignatureVerificationError("A webhook signing secret is required.")

        parsed = _parse_header(sig_header) if sig_header else None
        if parsed is None:
            raise SignatureVerificationError(
                f'Unable to parse the {SIGNATURE_HEADER} header. Expected "t=<timestamp>,v1=<signature>".'
            )
        timestamp, signatures = parsed
        if not signatures:
            raise SignatureVerificationError(f"No v1 signatures found in the {SIGNATURE_HEADER} header.")

        current = int(time.time()) if now is None else now
        if tolerance > 0 and abs(current - timestamp) > tolerance:
            raise SignatureVerificationError(
                f"Webhook timestamp is outside the {tolerance}s tolerance — possible replay. "
                "Check your server clock if this repeats."
            )

        expected = _sign(secret, timestamp, body)
        if not any(hmac.compare_digest(expected, candidate) for candidate in signatures):
            raise SignatureVerificationError(
                f"No signature matches the expected signature for this payload. Check the endpoint secret. {_RAW_BODY_HINT}"
            )

        try:
            data = json.loads(body)
        except ValueError as exc:
            raise SignatureVerificationError("Webhook payload is not valid JSON.") from exc
        if isinstance(data, dict) and str(data.get("event", "")).startswith("payment."):
            try:
                return PaymentEvent.model_validate(data)
            except ValidationError:
                pass  # unexpected payment shape — still hand back the verified event
        try:
            return GenericEvent.model_validate(data)
        except ValidationError as exc:
            raise SignatureVerificationError("Webhook payload is not a VEXPay event envelope.") from exc

    @staticmethod
    def generate_test_header(payload: str, secret: str, timestamp: Optional[int] = None) -> str:
        """Build a valid ``VexPay-Signature`` value — for your own tests."""
        ts = int(time.time()) if timestamp is None else timestamp
        return f"t={ts},v1={_sign(secret, ts, payload)}"
