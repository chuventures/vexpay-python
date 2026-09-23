from __future__ import annotations

import re
from typing import Any, Optional

import pytest

import vexpay
from vexpay import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AsyncVexPay,
    AuthenticationError,
    ConfigurationError,
    ConflictError,
    InvalidRequestError,
    NotFoundError,
    RateLimitError,
    VexPay,
    VexPayError,
)
from vexpay._core import AsyncHttp, SyncHttp, _Config, backoff_delay, parse_retry_after

from .conftest import MockServer, Scripted, async_sleeps_recorder, sleeps_recorder


def sync_http(server: MockServer, *, retries: int = 2, timeout: float = 5.0) -> tuple[SyncHttp, list[float]]:
    sleeps, sleep = sleeps_recorder()
    return SyncHttp(_Config("sk_test_123", server.url, timeout, retries), sleep=sleep), sleeps


def async_http(server: MockServer, *, retries: int = 2, timeout: float = 5.0) -> tuple[AsyncHttp, list[float]]:
    sleeps, sleep = async_sleeps_recorder()
    return AsyncHttp(_Config("sk_test_123", server.url, timeout, retries), sleep=sleep), sleeps


# ── configuration ──────────────────────────────────────────────────────────────


def test_requires_an_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VEXPAY_API_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="API key is required"):
        VexPay()
    with pytest.raises(ConfigurationError):
        AsyncVexPay(api_key="   ")


def test_reads_the_key_from_the_environment(monkeypatch: pytest.MonkeyPatch, server: MockServer) -> None:
    monkeypatch.setenv("VEXPAY_API_KEY", "sk_env")
    server.script([Scripted(200, [])])
    with VexPay(base_url=server.url) as client:
        client._http.request("GET", "/v1/banks")
    assert server.requests[0].headers["x-api-key"] == "sk_env"


# ── request core ───────────────────────────────────────────────────────────────


def test_sends_key_user_agent_and_json(server: MockServer) -> None:
    server.script([Scripted(201, {"ok": True})])
    http, _ = sync_http(server)
    assert http.request("POST", "/v1/quote", body={"usdAmount": 10}) == {"ok": True}

    req = server.requests[0]
    assert req.headers["x-api-key"] == "sk_test_123"
    assert re.match(rf"^vexpay-python/{re.escape(vexpay.__version__)} python/3\.", req.headers["user-agent"])
    assert req.headers["content-type"] == "application/json"
    assert req.body == {"usdAmount": 10}


def test_serializes_query_and_skips_none(server: MockServer) -> None:
    server.script([Scripted(200, {})])
    http, _ = sync_http(server)
    http.request("GET", "/v1/merchants", query={"limit": 25, "cursor": None, "isActive": True})
    assert server.requests[0].path == "/v1/merchants?limit=25&isActive=true"


def test_empty_success_body_is_none(server: MockServer) -> None:
    server.script([Scripted(204)])
    http, _ = sync_http(server)
    assert http.request("DELETE", "/v1/webhooks/x") is None


def test_pydantic_bodies_send_only_fields_the_caller_set(server: MockServer) -> None:
    from vexpay._generated.models import CreateCheckoutSessionDto

    server.script([Scripted(201, {})])
    http, _ = sync_http(server)
    http.request("POST", "/v1/checkout/sessions", body=CreateCheckoutSessionDto(amountUsd=25))
    assert server.requests[0].body == {"amountUsd": 25.0}


# ── error mapping ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("status", "body", "error_class", "code", "message"),
    [
        (400, {"statusCode": 400, "message": ["usdAmount must be positive"], "error": "Bad Request"}, InvalidRequestError, None, "usdAmount must be positive"),
        (401, {"statusCode": 401, "message": "Invalid or inactive API key", "error": "Unauthorized"}, AuthenticationError, None, "Invalid or inactive API key"),
        (403, {"message": "Forbidden"}, InvalidRequestError, None, "Forbidden"),
        (404, {"error": "not_found"}, NotFoundError, "not_found", "not_found"),
        (409, {"error": "external_ref_conflict", "message": "externalRef reused"}, ConflictError, "external_ref_conflict", "externalRef reused"),
        (422, {"error": "insufficient_balance"}, InvalidRequestError, "insufficient_balance", "insufficient_balance"),
    ],
)
def test_maps_error_responses(
    server: MockServer,
    status: int,
    body: dict[str, Any],
    error_class: type[VexPayError],
    code: Optional[str],
    message: str,
) -> None:
    server.script([Scripted(status, body, {"x-request-id": "req_42"})])
    http, _ = sync_http(server)
    with pytest.raises(error_class) as info:
        http.request("POST", "/v1/payouts", body={})
    err = info.value
    assert isinstance(err, VexPayError)
    assert (err.status, err.code, err.body, err.request_id, err.message) == (status, code, body, "req_42", message)
    assert len(server.requests) == 1  # never retried


def test_rate_limit_surfaces_after_retries(server: MockServer) -> None:
    server.script([Scripted(429, {"message": "slow down"})])
    http, _ = sync_http(server, retries=1)
    with pytest.raises(RateLimitError):
        http.request("GET", "/v1/banks")
    assert len(server.requests) == 2


def test_5xx_surfaces_as_api_error_after_retries(server: MockServer) -> None:
    server.script([Scripted(503, {"message": "bank down"})])
    http, _ = sync_http(server)
    with pytest.raises(APIError) as info:
        http.request("GET", "/v1/banks")
    assert (info.value.status, info.value.message) == (503, "bank down")
    assert len(server.requests) == 3


def test_unreachable_host_is_a_connection_error() -> None:
    sleeps, sleep = sleeps_recorder()
    http = SyncHttp(_Config("k", "http://127.0.0.1:1", 2.0, 2), sleep=sleep)
    with pytest.raises(APIConnectionError) as info:
        http.request("GET", "/v1/banks")
    assert not isinstance(info.value, APITimeoutError)
    assert len(sleeps) == 2


def test_slow_answer_is_a_timeout(server: MockServer) -> None:
    server.script([Scripted(200, {}, delay=0.5)])
    http, _ = sync_http(server, retries=0, timeout=0.05)
    with pytest.raises(APITimeoutError):
        http.request("GET", "/v1/banks")


# ── idempotency and retries ────────────────────────────────────────────────────


def test_one_idempotency_key_across_all_attempts(server: MockServer) -> None:
    server.script([Scripted(503), Scripted(502), Scripted(201, {"paymentId": "p1"})])
    http, _ = sync_http(server)
    assert http.request("POST", "/v1/payments/c2p", body={"token": "123456"}) == {"paymentId": "p1"}
    keys = [r.headers.get("idempotency-key") for r in server.requests]
    assert len(keys) == 3 and len(set(keys)) == 1
    assert re.match(r"^[0-9a-f-]{36}$", keys[0] or "")


def test_caller_supplied_idempotency_key(server: MockServer) -> None:
    server.script([Scripted(201, {})])
    http, _ = sync_http(server)
    http.request("POST", "/v1/payouts", body={}, options={"idempotency_key": "order-1042-charge"})
    assert server.requests[0].headers["idempotency-key"] == "order-1042-charge"


def test_separate_calls_get_separate_keys_and_gets_get_none(server: MockServer) -> None:
    server.script([Scripted(201, {})])
    http, _ = sync_http(server)
    http.request("POST", "/v1/payouts", body={})
    http.request("POST", "/v1/payouts", body={})
    http.request("GET", "/v1/payouts")
    a, b, get = (r.headers.get("idempotency-key") for r in server.requests)
    assert a != b and get is None


def test_retries_in_progress_conflict_with_same_key(server: MockServer) -> None:
    server.script([Scripted(409, {"error": "idempotency_request_in_progress"}), Scripted(201, {"paymentId": "p1"})])
    http, _ = sync_http(server)
    assert http.request("POST", "/v1/payments/c2p", body={}) == {"paymentId": "p1"}
    assert server.requests[0].headers["idempotency-key"] == server.requests[1].headers["idempotency-key"]


def test_does_not_retry_other_conflicts(server: MockServer) -> None:
    server.script([Scripted(409, {"error": "idempotency_key_reused"})])
    http, _ = sync_http(server)
    with pytest.raises(ConflictError) as info:
        http.request("POST", "/v1/payouts", body={})
    assert info.value.code == "idempotency_key_reused"
    assert len(server.requests) == 1


def test_honours_retry_after(server: MockServer) -> None:
    server.script([Scripted(429, None, {"retry-after": "3"}), Scripted(200, {})])
    http, sleeps = sync_http(server)
    http.request("GET", "/v1/banks")
    assert sleeps == [3.0]


def test_backs_off_with_jitter(server: MockServer) -> None:
    server.script([Scripted(500), Scripted(500), Scripted(200, {})])
    http, sleeps = sync_http(server)
    http.request("GET", "/v1/banks")
    assert len(sleeps) == 2
    assert 0.25 <= sleeps[0] <= 0.5
    assert 0.5 <= sleeps[1] <= 1.0


def test_max_network_retries_zero(server: MockServer) -> None:
    server.script([Scripted(500)])
    http, _ = sync_http(server, retries=0)
    with pytest.raises(APIError):
        http.request("GET", "/v1/banks")
    assert len(server.requests) == 1


def test_per_call_retry_override(server: MockServer) -> None:
    server.script([Scripted(500)])
    http, _ = sync_http(server, retries=2)
    with pytest.raises(APIError):
        http.request("GET", "/v1/banks", options={"max_network_retries": 0})
    assert len(server.requests) == 1


def test_never_retries_validation_errors(server: MockServer) -> None:
    server.script([Scripted(400, {"message": "bad"})])
    http, _ = sync_http(server)
    with pytest.raises(InvalidRequestError):
        http.request("POST", "/v1/quote", body={})
    assert len(server.requests) == 1


def test_retry_helpers() -> None:
    import email.utils

    now = 1_790_000_000.0
    assert parse_retry_after("2", now) == 2.0
    assert parse_retry_after(email.utils.formatdate(now + 5, usegmt=True), now) == 5.0
    assert parse_retry_after("9999", now) == 60.0
    assert parse_retry_after("soon", now) is None
    assert parse_retry_after(None, now) is None
    assert backoff_delay(10, lambda: 1.0) == 8.0
    assert backoff_delay(0, lambda: 0.0) == 0.25


# ── async parity ───────────────────────────────────────────────────────────────


async def test_async_same_key_across_retries(server: MockServer) -> None:
    server.script([Scripted(503), Scripted(201, {"paymentId": "p1"})])
    http, sleeps = async_http(server)
    assert await http.request("POST", "/v1/payments/c2p", body={}) == {"paymentId": "p1"}
    assert server.requests[0].headers["idempotency-key"] == server.requests[1].headers["idempotency-key"]
    assert len(sleeps) == 1
    await http.aclose()


async def test_async_error_mapping(server: MockServer) -> None:
    server.script([Scripted(422, {"error": "insufficient_balance"})])
    http, _ = async_http(server)
    with pytest.raises(InvalidRequestError) as info:
        await http.request("POST", "/v1/payouts", body={})
    assert (info.value.status, info.value.code) == (422, "insufficient_balance")
    await http.aclose()


async def test_async_timeout(server: MockServer) -> None:
    server.script([Scripted(200, {}, delay=0.5)])
    http, _ = async_http(server, retries=0, timeout=0.05)
    with pytest.raises(APITimeoutError):
        await http.request("GET", "/v1/banks")
    await http.aclose()


async def test_async_client_context_manager(server: MockServer) -> None:
    server.script([Scripted(200, [])])
    async with AsyncVexPay("sk_test_async", base_url=server.url) as client:
        assert await client._http.request("GET", "/v1/banks") == []
