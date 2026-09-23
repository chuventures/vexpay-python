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
