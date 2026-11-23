from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pytest

from vexpay import (
    WEBHOOK_EVENT_NAMES,
    GenericEvent,
    PaymentEvent,
    SignatureVerificationError,
    VexPay,
    Webhook,
)

FIXTURES = Path(__file__).resolve().parent.parent.parent / "sdk-spec" / "fixtures"
VECTORS: dict[str, Any] = json.loads((FIXTURES / "webhook-signatures.json").read_text())


def verify(case: dict[str, Any]) -> Any:
    return Webhook.construct_event(
        case["body"], case["header"], VECTORS["secret"], VECTORS["toleranceSeconds"], now=VECTORS["now"]
    )


@pytest.mark.parametrize("case", VECTORS["cases"], ids=[c["name"] for c in VECTORS["cases"]])
def test_conformance_vectors(case: dict[str, Any]) -> None:
    if case["valid"]:
        event = verify(case)
        assert isinstance(event, PaymentEvent)
        assert event.event == "payment.completed"
    else:
        with pytest.raises(SignatureVerificationError):
            verify(case)


def _case(name: str) -> dict[str, Any]:
    return next(c for c in VECTORS["cases"] if c["name"] == name)


def test_accepts_bytes_and_types_payment_data() -> None:
    valid = _case("valid")
    event = Webhook.construct_event(valid["body"].encode(), valid["header"], VECTORS["secret"], now=VECTORS["now"])
    assert isinstance(event, PaymentEvent)
    assert event.data.status == "COMPLETED"
    assert event.data.livemode is False


def test_explains_raw_body_on_mismatch() -> None:
    with pytest.raises(SignatureVerificationError, match="raw request body"):
        verify(_case("re-serialized body (key order changed)"))


def test_refuses_parsed_payload() -> None:
    valid = _case("valid")
    with pytest.raises(SignatureVerificationError, match="raw body"):
        Webhook.construct_event(json.loads(valid["body"]), valid["header"], VECTORS["secret"], now=VECTORS["now"])  # type: ignore[arg-type]


def test_tolerance_message_and_override() -> None:
    stale = _case("stale timestamp")
    with pytest.raises(SignatureVerificationError, match="outside the 300s tolerance"):
        verify(stale)
    assert Webhook.construct_event(stale["body"], stale["header"], VECTORS["secret"], 900, now=VECTORS["now"])


def test_real_clock_default_tolerance() -> None:
    payload = json.dumps({"event": "notification.test", "data": {"livemode": False}, "timestamp": "x"})
    fresh = Webhook.generate_test_header(payload, "s")
    old = Webhook.generate_test_header(payload, "s", timestamp=int(time.time()) - 600)
    assert isinstance(Webhook.construct_event(payload, fresh, "s"), GenericEvent)
    with pytest.raises(SignatureVerificationError):
        Webhook.construct_event(payload, old, "s")


def test_unknown_future_event_still_verifies() -> None:
    payload = json.dumps({"event": "dispute.opened", "data": {"livemode": True}, "timestamp": "x"})
    header = Webhook.generate_test_header(payload, "s", timestamp=1_790_000_000)
    event = Webhook.construct_event(payload, header, "s", now=1_790_000_000)
    assert isinstance(event, GenericEvent) and event.event == "dispute.opened"


def test_available_on_the_client() -> None:
    valid = _case("valid")
    client = VexPay("k")
    assert client.webhooks.construct_event(valid["body"], valid["header"], VECTORS["secret"], now=VECTORS["now"])


def test_event_names_match_api_fixture() -> None:
    events = json.loads((FIXTURES / "webhook-events.json").read_text())["events"]
    assert list(WEBHOOK_EVENT_NAMES) == events


def _deliver(event: str, data: dict[str, Any]) -> Any:
    payload = json.dumps({"event": event, "data": {"livemode": True, **data}, "timestamp": "t"})
    header = Webhook.generate_test_header(payload, "whsec", timestamp=1_790_000_000)
    return Webhook.construct_event(payload, header, "whsec", now=1_790_000_000)


def test_partial_pago_movil_pending_carries_progress() -> None:
    # pago-movil-partial-webhooks: one payment.pending per transfer that does not complete it yet.
    event = _deliver(
        "payment.pending",
        {
            "paymentId": "pay-1",
            "status": "PENDING",
            "method": "PAGO_MOVIL",
            "vesAmount": 1837.53,
            "paidVesAmount": 1500,
            "missingVesAmount": 337.53,
            "expiresAt": "2026-11-24T01:47:26.112Z",
            "transfers": [{"reference": "063269956294", "vesAmount": 1500, "at": "2026-11-23T01:47:26.111Z"}],
        },
    )
    assert isinstance(event, PaymentEvent)
    assert event.data.paidVesAmount == 1500
    assert event.data.missingVesAmount == 337.53
    assert event.data.transfers is not None and event.data.transfers[0].reference == "063269956294"
    assert event.data.refundPending is None


def test_expired_partial_failed_says_refund_pending() -> None:
    event = _deliver(
        "payment.failed",
        {"paymentId": "pay-1", "status": "FAILED", "failureCode": "expired", "paidVesAmount": 1500, "refundPending": True},
    )
    assert isinstance(event, PaymentEvent)
    assert event.data.refundPending is True
    assert event.data.paidVesAmount == 1500
