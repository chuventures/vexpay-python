from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest

from vexpay import APIError, AsyncVexPay, VexPay

from .conftest import MockServer, Recorded, Scripted


def paginated(total: int) -> Any:
    def handler(req: Recorded, _index: int) -> Scripted:
        qs = parse_qs(urlparse(req.path).query)
        limit = int(qs.get("limit", ["25"])[0])
        start = int(qs.get("cursor", ["0"])[0])
        end = min(start + limit, total)
        items = [_merchant(i) for i in range(start, end)]
        return Scripted(200, {"items": items, "nextCursor": str(end) if end < total else None})

    return handler


def _merchant(i: int) -> dict[str, Any]:
    return {
        "merchantId": f"mrc_{i}",
        "accountId": f"acct_{i}",
        "externalRef": f"m-{i}",
        "status": "verified",
        "isActive": True,
        "name": f"Merchant {i}",
        "identification": "V12345678",
        "createdAt": "2026-09-22T12:00:00.000Z",
    }


def _payout(payout_id: str) -> dict[str, Any]:
    return {"payoutId": payout_id, "status": "completed"}


def test_iterates_250_merchants_in_3_requests(server: MockServer) -> None:
    server.script(paginated(250))
    client = VexPay("k", base_url=server.url, max_network_retries=0)
    ids = [m.merchantId for m in client.merchants.list({"limit": 100})]

    assert len(ids) == 250 and ids[0] == "mrc_0" and ids[-1] == "mrc_249"
    assert [r.path for r in server.requests] == [
        "/v1/merchants?limit=100",
        "/v1/merchants?limit=100&cursor=100",
        "/v1/merchants?limit=100&cursor=200",
    ]


def test_list_returns_first_page(server: MockServer) -> None:
    server.script(paginated(250))
    page = VexPay("k", base_url=server.url).merchants.list({"limit": 100})
    assert len(page.items) == 100 and page.next_cursor == "100"
    assert len(server.requests) == 1


def test_starts_from_a_given_cursor(server: MockServer) -> None:
    server.script(paginated(250))
    rest = VexPay("k", base_url=server.url).merchants.list({"limit": 100, "cursor": "200"}).to_list()
    assert len(rest) == 50 and len(server.requests) == 1


def test_to_list_stops_at_limit(server: MockServer) -> None:
    server.script(paginated(250))
    first_120 = VexPay("k", base_url=server.url).merchants.list({"limit": 100}).to_list(limit=120)
    assert len(first_120) == 120 and len(server.requests) == 2


def test_stops_on_repeated_cursor(server: MockServer) -> None:
    server.script([Scripted(200, {"items": [_payout("p")], "nextCursor": "same"})])
    items = VexPay("k", base_url=server.url).payouts.list().to_list()
    assert len(items) == 2 and len(server.requests) == 2


def test_error_on_later_page_propagates(server: MockServer) -> None:
    server.script(
        lambda _req, i: Scripted(200, {"items": [_payout("a")], "nextCursor": "1"}) if i == 0 else Scripted(500, {"message": "down"})
    )
    seen: list[str] = []
    with pytest.raises(APIError):
        for payout in VexPay("k", base_url=server.url, max_network_retries=0).payouts.list():
            seen.append(payout.payoutId)
    assert seen == ["a"]


async def test_async_iterates_all_pages(server: MockServer) -> None:
    server.script(paginated(250))
    async with AsyncVexPay("k", base_url=server.url) as client:
        ids = [m.merchantId async for m in client.merchants.list({"limit": 100})]
    assert len(ids) == 250 and len(server.requests) == 3


async def test_async_await_gives_first_page_and_is_lazy(server: MockServer) -> None:
    server.script(paginated(250))
    async with AsyncVexPay("k", base_url=server.url) as client:
        pending = client.merchants.list({"limit": 100})
        assert server.requests == []
        page = await pending
        assert len(page.items) == 100 and page.nextCursor == "100"
        assert len(server.requests) == 1
        assert len(await client.merchants.list({"limit": 100}).to_list(limit=150)) == 150
