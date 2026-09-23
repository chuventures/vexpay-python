"""Shared conformance: error-mapping, pagination, and retry fixtures from sdk-spec.

Pass/fail must match the Node suite (``packages/sdk-node/test/conformance.test.ts``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

import pytest

from vexpay import (
    APIError,
    AuthenticationError,
    ConflictError,
    InvalidRequestError,
    NotFoundError,
    RateLimitError,
    VexPay,
    VexPayError,
)
from vexpay._core import SyncHttp, _Config

from .conftest import MockServer, Recorded, Scripted, sleeps_recorder

FIXTURES = Path(__file__).resolve().parent.parent.parent / "sdk-spec" / "fixtures"

ERROR_CLASS = {
    "invalid_request": InvalidRequestError,
    "authentication": AuthenticationError,
    "not_found": NotFoundError,
    "conflict": ConflictError,
    "rate_limit": RateLimitError,
    "api": APIError,
}


def _load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text())


# ── error mapping ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize("case", _load("error-mapping.json")["cases"], ids=lambda c: c["name"])
def test_error_mapping_fixture(server: MockServer, case: dict[str, Any]) -> None:
    fixture = _load("error-mapping.json")
    server.script([Scripted(case["status"], case["body"], {"x-request-id": fixture["requestId"]})])
    sleeps, sleep = sleeps_recorder()
    http = SyncHttp(
        _Config("sk_test", server.url, 5.0, case.get("maxNetworkRetries", 2)),
        sleep=sleep,
    )
    with pytest.raises(ERROR_CLASS[case["errorClass"]]) as info:
        http.request("POST", "/v1/payouts", body={})
    err = info.value
    assert isinstance(err, VexPayError)
    assert (err.status, err.code, err.body, err.request_id, err.message) == (
        case["status"],
        case["code"],
        case["body"],
        fixture["requestId"],
        case["message"],
    )
    assert len(server.requests) == 1
    assert sleeps == []


# ── pagination ─────────────────────────────────────────────────────────────────


def _paginated(total: int):
    def handler(req: Recorded, _index: int) -> Scripted:
        qs = parse_qs(urlparse(req.path).query)
        limit = int(qs.get("limit", ["25"])[0])
        start = int(qs.get("cursor", ["0"])[0])
        end = min(start + limit, total)
        items = [
            {
                "merchantId": f"mrc_{i}",
                "accountId": f"acct_{i}",
                "externalRef": f"m-{i}",
                "status": "verified",
                "isActive": True,
                "name": f"Merchant {i}",
                "identification": "V12345678",
                "createdAt": "2026-09-22T12:00:00.000Z",
            }
            for i in range(start, end)
        ]
        return Scripted(200, {"items": items, "nextCursor": str(end) if end < total else None})

    return handler


@pytest.mark.parametrize("case", _load("pagination.json")["cases"], ids=lambda c: c["name"])
def test_pagination_fixture(server: MockServer, case: dict[str, Any]) -> None:
    server.script(_paginated(case["total"]))
    client = VexPay("sk_test", base_url=server.url, max_network_retries=0)
    params: dict[str, Any] = {"limit": case["limit"]}
    if case["startCursor"]:
        params["cursor"] = case["startCursor"]
    ids = [m.merchantId for m in client.merchants.list(params)]
    expect = case["expect"]
    assert len(ids) == expect["itemCount"]
    assert ids[0] == expect["firstId"]
    assert ids[-1] == expect["lastId"]
    assert [r.path for r in server.requests] == expect["paths"]


# ── retries ────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("case", _load("retries.json")["cases"], ids=lambda c: c["name"])
def test_retries_fixture(server: MockServer, case: dict[str, Any]) -> None:
    fixture = _load("retries.json")
    server.script(
        [
            Scripted(r["status"], r.get("body"), r.get("headers") or {})
            for r in case["responses"]
        ]
    )
    sleeps, sleep = sleeps_recorder()
    http = SyncHttp(
        _Config(
            "sk_test",
            server.url,
            5.0,
            case.get("maxNetworkRetries", fixture["defaultMaxNetworkRetries"]),
        ),
        sleep=sleep,
    )
    options: Optional[dict[str, Any]] = None
    if case.get("idempotencyKey"):
        options = {"idempotency_key": case["idempotencyKey"]}

    expect = case["expect"]
    if "ok" in expect:
        result = http.request(
            case["method"],
            case["path"],
            body=case.get("body"),
            options=options,
        )
        assert result == expect["ok"]
    else:
        with pytest.raises(ERROR_CLASS[expect["errorClass"]]) as info:
            http.request(case["method"], case["path"], body=case.get("body"), options=options)
        if expect.get("code"):
            assert info.value.code == expect["code"]

    assert len(server.requests) == expect["requestCount"]
    keys = [r.headers.get("idempotency-key") for r in server.requests]
    if expect.get("sameIdempotencyKey"):
        assert len(set(keys)) == 1 and keys[0]
    if expect.get("idempotencyKeyPresent") is True:
        assert keys[0] and len(keys[0]) == 36
    if expect.get("idempotencyKeyPresent") is False:
        assert keys[0] is None
    if expect.get("idempotencyKey"):
        assert keys[0] == expect["idempotencyKey"]
    if "retryAfterSeconds" in expect:
        assert sleeps == [float(expect["retryAfterSeconds"])]
