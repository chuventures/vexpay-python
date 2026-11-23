"""Webhook deliveries/resend/rotate, payments list/export and one-shot payment links."""

from __future__ import annotations

from typing import Any

import pytest

from vexpay import AsyncVexPay, InvalidRequestError, VexPay
from vexpay._generated import models as m

from .conftest import MockServer, Recorded, Scripted

RECEIPT = {
    "paymentId": "00000000-0000-4000-8000-000000000001",
    "status": "COMPLETED",
    "method": "C2P",
    "usdAmount": 25,
    "vesAmount": 20000,
    "bcvRate": 800,
    "tenantName": "Tienda",
    "createdAt": "2026-11-20T12:00:00.000Z",
}


def _delivery(id: str, **extra: Any) -> dict[str, Any]:
    return {
        "id": id,
        "event": "payment.completed",
        "status": "retrying",
        "attempts": 2,
        "lastAttemptAt": "2026-11-23T12:00:00.000Z",
        "nextAttemptAt": "2026-11-23T12:05:00.000Z",
        "lastResponseStatus": 503,
        "lastResponseBody": "Service Unavailable",
        "createdAt": "2026-11-23T11:59:00.000Z",
        **extra,
    }


ONE_SHOT = {
    "id": "plk_1",
    "kind": "one_shot",
    "origin": "api",
    "url": "https://pay.vexpay.app/pay/torta-x7k2",
    "slug": "torta-x7k2",
    "status": "ACTIVE",
    "amount": "25.00",
    "currency": "USD",
    "description": "Torta de chocolate",
    "reference": "order-1042",
    "createdAt": "2026-11-23T12:00:00.000Z",
    "expiresAt": None,
    "paidAt": None,
    "paymentId": None,
}

PRODUCT_LINK = {
    "id": "pl_1",
    "kind": "product",
    "productId": "prod_1",
    "slug": "camiseta",
    "hostedCheckoutPath": "/pay/camiseta",
    "status": "active",
    "allowQuantity": False,
    "createdAt": "2026-11-23T12:00:00.000Z",
}


def test_webhook_deliveries_resend_and_rotate(server: MockServer) -> None:
    server.script([
        Scripted(200, {"items": [_delivery("d_1"), _delivery("d_2")], "nextCursor": "c2"}),
        Scripted(200, {"items": [_delivery("d_3")], "nextCursor": None}),
        Scripted(202, _delivery("d_1", status="success", nextAttemptAt=None)),
        Scripted(200, {"id": "we_1", "secret": "whsec_new", "previousSecretExpiresAt": "2026-11-24T12:00:00.000Z"}),
        Scripted(200, {"id": "we_1", "secret": "whsec_newer", "previousSecretExpiresAt": None}),
    ])
    client = VexPay("k", base_url=server.url)

    ids = [d.id for d in client.webhook_endpoints.list_deliveries("we_1", {"status": "retrying", "limit": 2})]
    assert ids == ["d_1", "d_2", "d_3"]
    assert server.requests[0].path == "/v1/webhooks/we_1/deliveries?status=retrying&limit=2"
    assert server.requests[1].path == "/v1/webhooks/we_1/deliveries?status=retrying&limit=2&cursor=c2"

    resent = client.webhook_endpoints.resend_delivery("we_1", "d_1", idempotency_key="resend-1")
    assert resent.status == "success" and resent.nextAttemptAt is None
    assert (server.requests[2].method, server.requests[2].path) == ("POST", "/v1/webhooks/we_1/deliveries/d_1/resend")
    assert server.requests[2].headers["idempotency-key"] == "resend-1"

    rotated = client.webhook_endpoints.rotate_secret("we_1")
    assert isinstance(rotated, m.RotateWebhookSecretResponseDto) and rotated.secret == "whsec_new"
    assert server.requests[3].body == {}
    client.webhook_endpoints.rotate_secret("we_1", {"expiresInHours": 0})
    assert server.requests[4].body == {"expiresInHours": 0}


def test_payments_list_and_export(server: MockServer) -> None:
    csv = "id,createdAt,completedAt,status\n1,2026-11-20T12:00:00.000Z,,COMPLETED\n"
    server.script([
        Scripted(200, {"items": [RECEIPT], "nextCursor": "c2"}),
        Scripted(200, {"items": [RECEIPT], "nextCursor": None}),
        Scripted(200, csv, headers={"content-type": "text/csv"}),
    ])
    client = VexPay("k", base_url=server.url)
    page = client.payments.list({"status": "COMPLETED", "createdFrom": "2026-11-20", "limit": 1})
    assert [p.paymentId for p in page.items] == [RECEIPT["paymentId"]]
    assert len(page.to_list()) == 2
    assert server.requests[0].path == "/v1/payments?status=COMPLETED&createdFrom=2026-11-20&limit=1"
    assert server.requests[1].path == "/v1/payments?status=COMPLETED&createdFrom=2026-11-20&limit=1&cursor=c2"

    assert client.payments.export({"status": "COMPLETED"}) == csv
    assert server.requests[2].path == "/v1/payments/export?status=COMPLETED"


def test_export_refusal_carries_code_and_doc_url(server: MockServer) -> None:
    server.script([
        Scripted(
            400,
            {
                "statusCode": 400,
                "error": "export_range_too_long",
                "message": "At most 366 days",
                "code": "export_range_too_long",
                "docUrl": "https://docs.vexpay.app/errors#export_range_too_long",
            },
        )
    ])
    client = VexPay("k", base_url=server.url)
    with pytest.raises(InvalidRequestError) as info:
        client.payments.export({"createdFrom": "2024-01-01"})
    assert info.value.code == "export_range_too_long"
    assert info.value.doc_url == "https://docs.vexpay.app/errors#export_range_too_long"


def test_one_shot_payment_links(server: MockServer) -> None:
    def handler(req: Recorded, _index: int) -> Scripted:
        if req.method == "GET" and req.path.startswith("/v1/payment-links?"):
            return Scripted(200, {"items": [ONE_SHOT, PRODUCT_LINK], "nextCursor": None})
        if req.path.endswith("/cancel"):
            return Scripted(200, {**ONE_SHOT, "status": "CANCELLED"})
        if req.path == "/v1/payment-links/pl_1":
            return Scripted(200, PRODUCT_LINK)
        return Scripted(201 if req.method == "POST" else 200, ONE_SHOT)

    server.script(handler)
    client = VexPay("k", base_url=server.url)

    link = client.payment_links.create(
        {"amount": "25.00", "description": "Torta de chocolate", "reference": "order-1042"},
        idempotency_key="link-1",
    )
    assert isinstance(link, m.OneShotPaymentLinkDto) and link.url == ONE_SHOT["url"]
    assert server.requests[0].body == {"amount": "25.00", "description": "Torta de chocolate", "reference": "order-1042"}
    assert server.requests[0].headers["idempotency-key"] == "link-1"

    items = client.payment_links.list({"limit": 10}).items
    assert [type(item) for item in items] == [m.OneShotPaymentLinkDto, m.PaymentLinkResponseDto]
    assert server.requests[1].path == "/v1/payment-links?limit=10"

    assert isinstance(client.payment_links.retrieve("plk_1"), m.OneShotPaymentLinkDto)
    assert isinstance(client.payment_links.retrieve("pl_1"), m.PaymentLinkResponseDto)
    assert client.payment_links.cancel("plk_1").status == "CANCELLED"
    assert (server.requests[-1].method, server.requests[-1].path) == ("POST", "/v1/payment-links/plk_1/cancel")


async def test_async_new_resources(server: MockServer) -> None:
    server.script([
        Scripted(200, {"items": [_delivery("d_1")], "nextCursor": None}),
        Scripted(200, {"items": [RECEIPT], "nextCursor": None}),
        Scripted(200, "id\n1\n"),
        Scripted(200, ONE_SHOT),
    ])
    client = AsyncVexPay("k", base_url=server.url)
    assert [d.id async for d in client.webhook_endpoints.list_deliveries("we_1")] == ["d_1"]
    assert (await client.payments.list()).items[0].paymentId == RECEIPT["paymentId"]
    assert await client.payments.export() == "id\n1\n"
    assert (await client.payment_links.retrieve("plk_1")).kind == "one_shot"
    await client.aclose()
