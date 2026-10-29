from __future__ import annotations

import inspect
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Union

import pydantic
import pytest

from vexpay import AsyncPage, AsyncVexPay, ConflictError, InvalidRequestError, SyncPage, VexPay
from vexpay._generated.routes import RESPONSE_MODELS, ROUTES
from vexpay._resource import AsyncAPIResource, SyncAPIResource

from .conftest import MockServer, Scripted

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = json.loads((ROOT.parent / "sdk-spec" / "openapi.json").read_text())
SNAPSHOT_OPERATIONS = {
    op["operationId"]
    for item in SNAPSHOT["paths"].values()
    for op in item.values()
    if isinstance(op, dict) and "operationId" in op
}
PATH_ARG_NAMES = {"id", "merchant_id", "method_id", "external_ref", "customer_id"}


def resource_methods(root: object, prefix: str = "") -> list[tuple[str, Any]]:
    found: list[tuple[str, Any]] = []
    for key, value in vars(root).items():
        if not isinstance(value, (SyncAPIResource, AsyncAPIResource)):
            continue
        path = f"{prefix}.{key}" if prefix else key
        for name, fn in inspect.getmembers(type(value), inspect.isfunction):
            if name.startswith("_") or fn.__qualname__.split(".")[0] != type(value).__name__:
                continue
            found.append((f"{path}.{name}", getattr(value, name)))
        found.extend(resource_methods(value, path))
    return found


def dummy_args(fn: Any) -> list[Any]:
    args: list[Any] = []
    for param in inspect.signature(fn).parameters.values():
        if param.kind is inspect.Parameter.VAR_KEYWORD:
            continue
        if param.name in PATH_ARG_NAMES:
            args.append(f"{param.name}_1")
        elif param.name == "params":
            args.append({})
    return args


def operation_for(method: str, url: str) -> Optional[str]:
    path = url.split("?")[0]
    matches = [
        (op, template)
        for op, (verb, template) in ROUTES.items()
        if verb == method and re.fullmatch(re.sub(r"\{\w+\}", "[^/]+", template), path)
    ]
    matches.sort(key=lambda item: item[1].count("{"))
    return matches[0][0] if matches else None


def test_route_table_matches_snapshot() -> None:
    assert set(ROUTES) == SNAPSHOT_OPERATIONS
    assert set(RESPONSE_MODELS) == SNAPSHOT_OPERATIONS


def test_every_operation_reachable_sync(server: MockServer) -> None:
    server.script([Scripted(200, {})])
    client = VexPay("sk_test_cov", base_url=server.url, max_network_retries=0)
    covered: set[str] = set()
    for name, fn in resource_methods(client):
        before = len(server.requests)
        try:
            fn(*dummy_args(fn))
        except pydantic.ValidationError:
            pass  # the mock answers {} — routing is what is under test
        assert len(server.requests) == before + 1, f"{name} should send exactly one request"
        req = server.requests[-1]
        op = operation_for(req.method, req.path)
        assert op, f"{name} → {req.method} {req.path} matches no operation"
        covered.add(op)
    assert SNAPSHOT_OPERATIONS - covered == set()


async def test_every_operation_reachable_async(server: MockServer) -> None:
    server.script([Scripted(200, {})])
    client = AsyncVexPay("sk_test_cov", base_url=server.url, max_network_retries=0)
    covered: set[str] = set()
    for name, fn in resource_methods(client):
        before = len(server.requests)
        try:
            result = fn(*dummy_args(fn))
            if inspect.isawaitable(result):
                await result
        except pydantic.ValidationError:
            pass
        assert len(server.requests) == before + 1, f"{name} should send exactly one request"
        req = server.requests[-1]
        op = operation_for(req.method, req.path)
        assert op, f"{name} → {req.method} {req.path} matches no operation"
        covered.add(op)
    assert SNAPSHOT_OPERATIONS - covered == set()
    await client.aclose()


def test_sync_and_async_expose_the_same_methods() -> None:
    sync_names = {name for name, _ in resource_methods(VexPay("k"))}
    async_names = {name for name, _ in resource_methods(AsyncVexPay("k"))}
    assert sync_names == async_names


def test_async_resources_are_generated_from_sync() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_async.py"), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_substitutes_and_encodes_path_params(server: MockServer) -> None:
    server.script([Scripted(200, {})])
    client = VexPay("k", base_url=server.url)
    with pytest.raises(pydantic.ValidationError):
        client.merchants.payout_methods.confirm_verification("mrc/1", "pm 2", {"amounts": ["0.11"]})
    assert server.requests[-1].path == "/v1/merchants/mrc%2F1/payout-methods/pm%202/verify"


def test_rejects_empty_path_param_before_sending(server: MockServer) -> None:
    client = VexPay("k", base_url=server.url)
    with pytest.raises(InvalidRequestError, match='Missing required path parameter "id"'):
        client.payments.retrieve("")
    assert server.requests == []


RECEIPT = {
    "paymentId": "00000000-0000-4000-8000-000000000001",
    "status": "COMPLETED",
    "method": "C2P",
    "usdAmount": 25,
    "vesAmount": 20000,
    "bcvRate": 800,
    "tenantName": "Tienda",
    "createdAt": "2026-09-22T12:00:00.000Z",
}


def test_returns_validated_models(server: MockServer) -> None:
    server.script([Scripted(201, RECEIPT)])
    client = VexPay("k", base_url=server.url)
    receipt = client.payments.c2p.execute(
        {"usdAmount": 25, "debtorId": "V12345678", "debtorCellPhone": "584141234567", "debtorBankCode": 102, "token": "123456"}
    )
    assert type(receipt).__name__ == "PaymentReceiptDto"
    assert receipt.status == "COMPLETED"
    assert receipt.bcvRate == 800


RECEIVING_ACCOUNT = {
    "provider": "r4",
    "bankCode": "0169",
    "bankName": "R4 Conecta",
    "phone": "04125555555",
    "identification": "13536734",
    "configured": True,
    "missing": [],
    "livemode": False,
}


def test_pago_movil_receiving_account(server: MockServer) -> None:
    server.script([Scripted(200, RECEIVING_ACCOUNT)])
    client = VexPay("k", base_url=server.url)
    account = client.payments.pago_movil.receiving_account()
    assert type(account).__name__ == "PagoMovilReceivingAccountDto"
    assert account.configured is True and account.phone == "04125555555"
    request = server.requests[-1]
    assert request.method == "GET"
    assert request.path == "/v1/payments/pago-movil/receiving-account"


async def test_async_pago_movil_receiving_account(server: MockServer) -> None:
    server.script([Scripted(200, {**RECEIVING_ACCOUNT, "configured": False, "phone": None, "missing": ["phone"]})])
    async with AsyncVexPay("k", base_url=server.url) as client:
        account = await client.payments.pago_movil.receiving_account()
    assert account.configured is False and account.phone is None and account.missing == ["phone"]


async def test_async_returns_models(server: MockServer) -> None:
    server.script([Scripted(200, RECEIPT)])
    async with AsyncVexPay("k", base_url=server.url) as client:
        receipt = await client.payments.retrieve("pay_1")
    assert receipt.paymentId == RECEIPT["paymentId"]


def test_list_methods_return_pages() -> None:
    sync_client, async_client = VexPay("k"), AsyncVexPay("k")
    for resource in ("merchants", "payouts", "products", "customers", "prices", "subscriptions", "invoices"):
        assert inspect.signature(getattr(getattr(sync_client, resource), "list")).return_annotation.startswith("SyncPage[")
        assert inspect.signature(getattr(getattr(async_client, resource), "list")).return_annotation.startswith("AsyncPage[")
    assert SyncPage and AsyncPage


def test_usdc_payout_and_balances(server: MockServer) -> None:
    payout = {
        "id": "po_1", "object": "crypto.payout", "currency": "USDC", "status": "processing", "network": "BASE",
        "address": "0x" + "a" * 40, "amount": "10.00", "fee": "0.10", "idempotencyKey": "k1", "internal": False,
        "createdAt": "2026-10-02T00:00:00.000Z",
    }
    balances = {"data": [
        {"currency": "USDT", "available": "1.00", "pendingPayout": "0.00", "availableUsdt": "1.00", "pendingPayoutUsdt": "0.00", "asOf": "2026-10-02T00:00:00.000Z"},
        {"currency": "USDC", "available": "4.37", "pendingPayout": "0.00", "asOf": "2026-10-02T00:00:00.000Z"},
    ]}
    server.script([
        Scripted(201, payout),
        Scripted(200, {"currency": "USDC", "available": "4.37", "pendingPayout": "0.00", "asOf": "2026-10-02T00:00:00.000Z"}),
        Scripted(200, balances),
    ])
    client = VexPay("k", base_url=server.url)
    created = client.crypto.payouts.create(
        {"currency": "USDC", "network": "BASE", "address": payout["address"], "amount": "10.00", "idempotencyKey": "k1"}
    )
    assert created.currency == "USDC" and created.amount == "10.00"
    assert server.requests[0].body["currency"] == "USDC"
    assert client.crypto.balance.retrieve({"currency": "USDC"}).available == "4.37"
    assert server.requests[1].path == "/v1/crypto/balance?currency=USDC"
    assert [b.currency for b in client.crypto.balances.list().data] == ["USDT", "USDC"]


CONVERSION = {
    "id": "c0a8f6a2-1111-4b7e-9a51-0f4a1e9a0001", "object": "conversion", "status": "PENDING", "reference": None,
    "rate": "998.8299", "marketRate": "979.2450", "spreadPercent": "2.0000", "rateSource": "market",
    "sourceCurrency": "VES", "sourceAmount": "10000.00", "sourceAmountVes": "10000.00", "targetAmountUsdt": "10.01",
    "origin": "api", "paymentId": None, "createdAt": "2026-10-03T00:00:00.000Z",
    "completedAt": None, "canceledAt": None, "cancelReason": None,
}


def test_conversions_quote_convert_list_cancel(server: MockServer) -> None:
    quote = {
        "id": "q1", "object": "conversion_quote", "rate": "998.8299", "marketRate": "979.2450", "spreadPercent": "2.0000",
        "rateSource": "market", "sourceCurrency": "VES", "sourceAmount": "10000.00", "sourceAmountVes": "10000.00",
        "targetAmountUsdt": "10.01", "expiresAt": "2026-10-03T00:01:00.000Z", "createdAt": "2026-10-03T00:00:00.000Z",
    }
    server.script([
        Scripted(201, quote),
        Scripted(201, CONVERSION),
        Scripted(200, {"items": [CONVERSION], "nextCursor": None}),
        Scripted(200, {**CONVERSION, "status": "CANCELED", "cancelReason": "canceled_by_tenant"}),
    ])
    client = VexPay("k", base_url=server.url)
    q = client.conversions.quotes.create({"sourceAmountVes": "10000.00"})
    assert q.targetAmountUsdt == "10.01"
    created = client.conversions.create({"quoteId": q.id}, idempotency_key="conv-1")
    assert created.status == "PENDING"
    assert server.requests[1].path == "/v1/conversions"
    assert server.requests[1].headers["idempotency-key"] == "conv-1"
    assert [c.id for c in client.conversions.list({"status": "PENDING"})] == [CONVERSION["id"]]
    assert server.requests[2].path == "/v1/conversions?status=PENDING"
    assert client.conversions.cancel(CONVERSION["id"]).status == "CANCELED"
    assert server.requests[3].path == f"/v1/conversions/{CONVERSION['id']}/cancel"



def test_conversions_cop_quote_and_settings(server: MockServer) -> None:
    cop_quote = {
        "id": "q2", "object": "conversion_quote", "rate": "4037.6000", "marketRate": "3920.0000", "spreadPercent": "3.0000",
        "rateSource": "market", "sourceCurrency": "COP", "sourceAmount": "1000000", "sourceAmountVes": None,
        "targetAmountUsdt": "247.67", "expiresAt": "2026-10-09T00:01:00.000Z", "createdAt": "2026-10-09T00:00:00.000Z",
    }
    settings = {
        "object": "conversion_settings", "enabled": True, "sourceCurrencies": {"VES": True, "COP": True},
        "spreadPercent": {"VES": "3.0000", "COP": "3.0000"}, "minimumUsdt": "10.00",
        "dailyMax": {"VES": None, "COP": None}, "autoConvert": {"COP": {"percent": 50}},
    }
    server.script([Scripted(201, cop_quote), Scripted(200, settings), Scripted(200, settings)])
    client = VexPay("k", base_url=server.url)
    q = client.conversions.quotes.create({"sourceCurrency": "COP", "sourceAmount": "1000000"})
    assert q.sourceAmount == "1000000" and q.sourceAmountVes is None
    assert server.requests[0].body == {"sourceCurrency": "COP", "sourceAmount": "1000000"}
    assert client.conversions.settings.retrieve().autoConvert.COP.percent == 50
    assert server.requests[1].path == "/v1/conversions/settings"
    client.conversions.settings.update({"autoConvert": {"COP": {"percent": 50}}})
    assert server.requests[2].method == "PATCH"
    assert server.requests[2].body == {"autoConvert": {"COP": {"percent": 50}}}

COP_PAYMENT = {
    "id": "5e0c7b1a-2222-4b7e-9a51-0f4a1e9a0002", "status": "pending", "method": "COP", "channel": "daviplata",
    "amountCop": 50000, "metadata": {}, "createdAt": "2026-10-08T00:00:00.000Z", "expiresAt": "2026-10-08T00:05:00.000Z",
}


def test_cop_payment_otp_cancel_refund_and_balance(server: MockServer) -> None:
    server.script([
        Scripted(201, {**COP_PAYMENT, "next": {"type": "submit_otp"}}),
        Scripted(200, {**COP_PAYMENT, "status": "completed", "feeCop": 1750}),
        Scripted(200, COP_PAYMENT),
        Scripted(200, {**COP_PAYMENT, "status": "canceled"}),
        Scripted(200, {**COP_PAYMENT, "status": "refunded"}),
        Scripted(200, {"availableCop": 96500, "pendingPayoutCop": 0, "asOf": "2026-10-08T00:00:00.000Z"}),
    ])
    client = VexPay("k", base_url=server.url)
    buyer = {"email": "juan@example.com", "phone": "3001234567", "documentType": "CC", "documentNumber": "1234567890"}
    payment = client.cop.payments.create(
        {"amountCop": 50000, "channel": "daviplata", "buyer": buyer}, idempotency_key="cop-1"
    )
    assert payment.next is not None and payment.next.type == "submit_otp"
    assert server.requests[0].path == "/v1/cop/payments"
    assert server.requests[0].headers["idempotency-key"] == "cop-1"
    assert server.requests[0].body["buyer"]["documentType"] == "CC"
    assert client.cop.payments.submit_otp(payment.id, {"otp": "123456"}).status == "completed"
    assert server.requests[1].path == f"/v1/cop/payments/{COP_PAYMENT['id']}/otp"
    assert server.requests[1].body == {"otp": "123456"}
    assert client.cop.payments.retrieve(payment.id).channel == "daviplata"
    assert client.cop.payments.cancel(payment.id).status == "canceled"
    assert client.cop.payments.refund(payment.id).status == "refunded"
    assert server.requests[4].path == f"/v1/cop/payments/{COP_PAYMENT['id']}/refund"
    assert client.cop.balance.retrieve().availableCop == 96500
    assert server.requests[5].path == "/v1/cop/balance"


def test_cop_channels_then_pse_redirect(server: MockServer) -> None:
    server.script([
        Scripted(200, {
            "channels": [{"channel": "pse", "label": "PSE", "needsBuyer": True, "needsTermsAcceptance": True, "checkoutOnly": False, "minAmountCop": 20000}],
            "pseBanks": [{"code": "1007", "name": "Bancolombia"}],
            "terms": {"termsUrl": "https://t", "personalDataUrl": "https://d"},
        }),
        Scripted(201, {**COP_PAYMENT, "channel": "pse", "next": {"type": "redirect", "url": "https://bank.example/pse"}}),
    ])
    client = VexPay("k", base_url=server.url)
    catalog = client.cop.channels()
    assert server.requests[0].path == "/v1/cop/channels"
    assert catalog.channels[0].needsTermsAcceptance is True
    assert catalog.pseBanks is not None and catalog.pseBanks[0].code == "1007"
    buyer = {
        "firstName": "Juan", "lastName": "Pérez", "personType": "natural", "email": "juan@example.com",
        "phone": "3001234567", "documentType": "CC", "documentNumber": "1234567890", "termsAccepted": True,
    }
    payment = client.cop.payments.create({"amountCop": 80000, "channel": "pse", "pse": {"bankCode": "1007"}, "buyer": buyer})
    assert payment.next is not None and payment.next.type == "redirect" and payment.next.url == "https://bank.example/pse"
    assert server.requests[1].body["pse"] == {"bankCode": "1007"}
    assert server.requests[1].body["buyer"]["termsAccepted"] is True


# ── billing ───────────────────────────────────────────────────────────────────

CUSTOMER = {
    "id": "cus_1", "object": "customer", "name": "Ana Pérez", "email": "ana@example.com", "emailStatus": "deliverable",
    "phone": "04141234567", "idNumber": "V12345678", "bankCode": "0102", "metadata": {"plan": "pro"},
    "testClock": None, "createdAt": "2026-10-20T00:00:00.000Z", "livemode": False,
}
PRICE = {
    "id": "price_1", "object": "price", "product": "prod_1", "unitAmountUsd": "10.00", "currency": "USD",
    "recurring": {"interval": "month", "intervalCount": 1}, "nickname": "Monthly", "active": True, "metadata": {},
    "createdAt": "2026-10-20T00:00:00.000Z", "livemode": False,
}
SUBSCRIPTION = {
    "id": "sub_1", "object": "subscription", "customer": "cus_1", "price": PRICE, "status": "active",
    "collectionMethod": "send_invoice", "collectionAttempts": None, "paymentMethod": None,
    "currentPeriodStart": "2026-10-20T00:00:00.000Z", "currentPeriodEnd": "2026-11-20T00:00:00.000Z",
    "trialStart": None, "trialEnd": None, "cancelAtPeriodEnd": False, "canceledAt": None, "cancellationReason": None,
    "latestInvoice": "in_1", "methods": ["c2p", "pago_movil"], "metadata": {},
    "createdAt": "2026-10-20T00:00:00.000Z", "livemode": False,
}
INVOICE = {
    "id": "in_1", "object": "invoice", "number": "K7Q2M9XA-0001", "status": "open", "customer": "cus_1",
    "subscription": "sub_1", "collectionMethod": "send_invoice", "amountDueUsd": "10.00", "amountPaidUsd": "0.00",
    "currency": "USD", "periodStart": "2026-10-20T00:00:00.000Z", "periodEnd": "2026-11-20T00:00:00.000Z",
    "dueDate": "2026-10-20T00:00:00.000Z", "attemptsTotal": 3, "attemptCount": 0, "nextPaymentAttempt": None,
    "paidAt": None, "paidOutOfBand": False, "paymentId": None, "billingFee": None,
    "hostedInvoiceUrl": "https://pay.example/i/in_1", "createdAt": "2026-10-20T00:00:00.000Z", "livemode": False,
}
SETUP_SESSION = {
    "id": "seti_1", "object": "setup_session", "url": "https://pay.example/setup/seti_1", "customer": "cus_1",
    "status": "open", "paymentMethod": None, "successUrl": None, "expiresAt": "2026-10-21T00:00:00.000Z",
    "createdAt": "2026-10-20T00:00:00.000Z", "livemode": False,
}
PAYMENT_METHOD = {
    "id": "pm_1", "object": "payment_method", "type": "domiciliacion", "customer": "cus_1", "status": "active",
    "phoneLast4": "4567", "bankCode": "0102", "createdAt": "2026-10-20T00:00:00.000Z",
    "activatedAt": "2026-10-20T00:00:00.000Z", "deactivatedAt": None, "detachedAt": None, "livemode": False,
}


def test_customers_crud_and_payment_methods(server: MockServer) -> None:
    server.script([
        Scripted(201, CUSTOMER),
        Scripted(200, {"items": [CUSTOMER], "nextCursor": "cus_1"}),
        Scripted(200, {"items": [{**CUSTOMER, "id": "cus_0"}], "nextCursor": None}),
        Scripted(200, CUSTOMER),
        Scripted(200, {**CUSTOMER, "phone": None}),
        Scripted(200, {"items": [PAYMENT_METHOD], "nextCursor": None}),
        Scripted(200, {"id": "cus_1", "deleted": True}),
    ])
    client = VexPay("k", base_url=server.url)
    created = client.customers.create({"name": "Ana Pérez", "email": "ana@example.com"}, idempotency_key="cus-1")
    assert type(created).__name__ == "CustomerResponseDto" and created.id == "cus_1"
    assert server.requests[0].method == "POST" and server.requests[0].path == "/v1/customers"
    assert server.requests[0].headers["idempotency-key"] == "cus-1"
    assert server.requests[0].body == {"name": "Ana Pérez", "email": "ana@example.com"}
    assert [c.id for c in client.customers.list({"email": "ana@example.com", "limit": 1})] == ["cus_1", "cus_0"]
    assert server.requests[1].path == "/v1/customers?email=ana%40example.com&limit=1"
    assert server.requests[2].path == "/v1/customers?email=ana%40example.com&limit=1&cursor=cus_1"
    assert client.customers.retrieve("cus_1").emailStatus == "deliverable"
    assert server.requests[3].path == "/v1/customers/cus_1"
    assert client.customers.update("cus_1", {"phone": None}).phone is None
    assert server.requests[4].method == "POST" and server.requests[4].body == {"phone": None}
    assert [pm.id for pm in client.customers.payment_methods.list("cus_1")] == ["pm_1"]
    assert server.requests[5].path == "/v1/customers/cus_1/payment-methods"
    assert client.customers.delete("cus_1").deleted is True
    assert server.requests[6].method == "DELETE" and server.requests[6].path == "/v1/customers/cus_1"


def test_prices_create_list_retrieve_update(server: MockServer) -> None:
    server.script([
        Scripted(201, PRICE),
        Scripted(200, {"items": [PRICE], "nextCursor": None}),
        Scripted(200, PRICE),
        Scripted(200, {**PRICE, "active": False}),
    ])
    client = VexPay("k", base_url=server.url)
    price = client.prices.create(
        {"product": "prod_1", "unitAmountUsd": "10.00", "recurring": {"interval": "month"}}, idempotency_key="price-1"
    )
    assert price.recurring.interval == "month" and price.unitAmountUsd == "10.00"
    assert server.requests[0].path == "/v1/prices" and server.requests[0].headers["idempotency-key"] == "price-1"
    assert [p.id for p in client.prices.list({"product": "prod_1", "active": "true"})] == ["price_1"]
    assert server.requests[1].path == "/v1/prices?product=prod_1&active=true"
    assert client.prices.retrieve("price_1").nickname == "Monthly"
    assert client.prices.update("price_1", {"active": False}).active is False
    assert server.requests[3].method == "POST" and server.requests[3].path == "/v1/prices/price_1"


def test_subscriptions_create_list_update_cancel(server: MockServer) -> None:
    server.script([
        Scripted(201, SUBSCRIPTION),
        Scripted(200, {"items": [SUBSCRIPTION], "nextCursor": None}),
        Scripted(200, SUBSCRIPTION),
        Scripted(200, {**SUBSCRIPTION, "cancelAtPeriodEnd": True}),
        Scripted(200, {**SUBSCRIPTION, "status": "canceled", "cancellationReason": "requested"}),
    ])
    client = VexPay("k", base_url=server.url)
    sub = client.subscriptions.create({"customer": "cus_1", "price": "price_1"}, idempotency_key="sub-1")
    assert type(sub).__name__ == "SubscriptionResponseDto" and sub.price.id == "price_1"
    assert server.requests[0].path == "/v1/subscriptions" and server.requests[0].headers["idempotency-key"] == "sub-1"
    assert [s.id for s in client.subscriptions.list({"customer": "cus_1", "status": "active"})] == ["sub_1"]
    assert server.requests[1].path == "/v1/subscriptions?customer=cus_1&status=active"
    assert client.subscriptions.retrieve("sub_1").latestInvoice == "in_1"
    assert client.subscriptions.update("sub_1", {"cancelAtPeriodEnd": True}).cancelAtPeriodEnd is True
    assert server.requests[3].method == "POST" and server.requests[3].path == "/v1/subscriptions/sub_1"
    canceled = client.subscriptions.cancel("sub_1")
    assert canceled.status == "canceled" and canceled.cancellationReason == "requested"
    assert server.requests[4].method == "DELETE" and server.requests[4].path == "/v1/subscriptions/sub_1"


def test_invoices_list_retrieve_and_actions(server: MockServer) -> None:
    server.script([
        Scripted(200, {"items": [INVOICE], "nextCursor": None}),
        Scripted(200, INVOICE),
        Scripted(200, {**INVOICE, "status": "void"}),
        Scripted(200, {**INVOICE, "status": "uncollectible"}),
        Scripted(200, {**INVOICE, "status": "paid", "paidOutOfBand": True, "amountPaidUsd": "10.00"}),
    ])
    client = VexPay("k", base_url=server.url)
    assert [i.number for i in client.invoices.list({"subscription": "sub_1", "status": "open"})] == ["K7Q2M9XA-0001"]
    assert server.requests[0].path == "/v1/invoices?subscription=sub_1&status=open"
    assert client.invoices.retrieve("in_1").amountDueUsd == "10.00"
    assert client.invoices.void("in_1", idempotency_key="void-1").status == "void"
    assert server.requests[2].method == "POST" and server.requests[2].path == "/v1/invoices/in_1/void"
    assert server.requests[2].headers["idempotency-key"] == "void-1"
    assert client.invoices.mark_uncollectible("in_1").status == "uncollectible"
    assert server.requests[3].path == "/v1/invoices/in_1/mark-uncollectible"
    paid = client.invoices.pay("in_1", {"paidOutOfBand": True})
    assert paid.status == "paid" and paid.paidOutOfBand is True
    assert server.requests[4].path == "/v1/invoices/in_1/pay" and server.requests[4].body == {"paidOutOfBand": True}


def test_setup_sessions_and_payment_methods(server: MockServer) -> None:
    server.script([
        Scripted(201, SETUP_SESSION),
        Scripted(200, {**SETUP_SESSION, "url": None, "status": "complete", "paymentMethod": "pm_1"}),
        Scripted(200, PAYMENT_METHOD),
        Scripted(200, {**PAYMENT_METHOD, "detachedAt": "2026-10-22T00:00:00.000Z"}),
    ])
    client = VexPay("k", base_url=server.url)
    session = client.setup_sessions.create({"customer": "cus_1"}, idempotency_key="seti-1")
    assert session.url == SETUP_SESSION["url"]
    assert server.requests[0].path == "/v1/setup-sessions" and server.requests[0].headers["idempotency-key"] == "seti-1"
    retrieved = client.setup_sessions.retrieve("seti_1")
    assert retrieved.url is None and retrieved.paymentMethod == "pm_1"
    assert server.requests[1].path == "/v1/setup-sessions/seti_1"
    assert client.payment_methods.retrieve("pm_1").phoneLast4 == "4567"
    assert server.requests[2].method == "GET" and server.requests[2].path == "/v1/payment-methods/pm_1"
    assert client.payment_methods.detach("pm_1").detachedAt is not None
    assert server.requests[3].method == "DELETE" and server.requests[3].path == "/v1/payment-methods/pm_1"


def test_bolivar_payment_method_list_is_unchanged(server: MockServer) -> None:
    server.script([Scripted(200, {"methods": []})])
    client = VexPay("k", base_url=server.url)
    with pytest.raises(pydantic.ValidationError):
        client.payments.methods()
    assert server.requests[-1].method == "GET" and server.requests[-1].path == "/v1/payment-methods"
    assert not hasattr(client.payment_methods, "list")


async def test_async_billing_resources(server: MockServer) -> None:
    server.script([
        Scripted(201, CUSTOMER),
        Scripted(200, {"items": [CUSTOMER], "nextCursor": None}),
        Scripted(200, {"items": [PAYMENT_METHOD], "nextCursor": None}),
        Scripted(201, PRICE),
        Scripted(200, {"items": [PRICE], "nextCursor": None}),
        Scripted(201, SUBSCRIPTION),
        Scripted(200, {"items": [SUBSCRIPTION], "nextCursor": None}),
        Scripted(200, {**SUBSCRIPTION, "status": "canceled"}),
        Scripted(200, {"items": [INVOICE], "nextCursor": None}),
        Scripted(200, {**INVOICE, "status": "paid", "paidOutOfBand": True}),
        Scripted(201, SETUP_SESSION),
        Scripted(200, PAYMENT_METHOD),
        Scripted(200, {"id": "cus_1", "deleted": True}),
    ])
    async with AsyncVexPay("k", base_url=server.url) as client:
        customer = await client.customers.create({"name": "Ana Pérez"}, idempotency_key="cus-1")
        assert customer.id == "cus_1"
        assert server.requests[0].headers["idempotency-key"] == "cus-1"
        page = await client.customers.list({"email": "ana@example.com"})
        assert [c.id for c in page.items] == ["cus_1"]
        assert [pm.id async for pm in client.customers.payment_methods.list("cus_1")] == ["pm_1"]
        assert server.requests[2].path == "/v1/customers/cus_1/payment-methods"
        assert (await client.prices.create({"product": "prod_1", "unitAmountUsd": "10.00"})).id == "price_1"
        assert [p.id for p in await client.prices.list().to_list()] == ["price_1"]
        assert (await client.subscriptions.create({"customer": "cus_1", "price": "price_1"})).status == "active"
        assert [s.id async for s in client.subscriptions.list({"customer": "cus_1"})] == ["sub_1"]
        assert (await client.subscriptions.cancel("sub_1")).status == "canceled"
        assert server.requests[7].method == "DELETE"
        assert [i.id async for i in client.invoices.list()] == ["in_1"]
        assert (await client.invoices.pay("in_1", {"paidOutOfBand": True})).paidOutOfBand is True
        assert server.requests[9].path == "/v1/invoices/in_1/pay"
        assert (await client.setup_sessions.create({"customer": "cus_1"})).status == "open"
        assert (await client.payment_methods.retrieve("pm_1")).status == "active"
        assert (await client.customers.delete("cus_1")).deleted is True
        assert server.requests[12].path == "/v1/customers/cus_1"



MERCHANT_ID = "5e0c7b1a-3333-4b7e-9a51-0f4a1e9a0003"
SELLER_BALANCE = {
    "merchantId": MERCHANT_ID, "accountId": "acct_1", "tenantId": "5e0c7b1a-4444-4b7e-9a51-0f4a1e9a0004",
    "pendingVes": "21540.00", "availableVes": "0.00", "paidOutVes": "0.00", "ledgerNetVes": "21540.00",
}
TRANSFER = {
    "transferKey": "q1-nov-u1", "amountVes": "21540.00", "amountUsd": "100.00", "rate": "215.4000",
    "rateSource": "bcv", "rateAsOf": "2026-11-03T00:00:00.000Z",
}


def _movement(movement_id: str) -> dict[str, Any]:
    return {
        "id": movement_id, "type": "credit", "amountVes": "21540.00", "description": "Credit",
        "transferKey": "q1-nov-u1", "amountUsd": "100.00", "rate": "215.4000", "rateSource": "bcv",
        "createdAt": "2026-11-03T12:00:00.000Z",
    }


STATEMENT = {
    "merchantId": MERCHANT_ID, "month": "2026-11", "from": "2026-11-01T04:00:00.000Z",
    "to": "2026-12-01T04:00:00.000Z", "openingVes": "0.00", "closingVes": "21540.00", "movements": [_movement("m1")],
}
STATEMENT_CSV = "date,type,amountVes,balanceVes\n2026-11-03T12:00:00.000Z,credit,21540.00,21540.00\n"


def test_merchant_usd_transfer_transactions_and_statement(server: MockServer) -> None:
    server.script([
        Scripted(200, {**SELLER_BALANCE, "transfer": TRANSFER}),
        Scripted(200, {"items": [_movement("m1"), _movement("m2")], "nextCursor": "c2"}),
        Scripted(200, {"items": [_movement("m3")], "nextCursor": None}),
        Scripted(200, STATEMENT),
        Scripted(200, STATEMENT_CSV, headers={"content-type": "text/csv"}),
    ])
    client = VexPay("k", base_url=server.url)
    result = client.merchants.transfer(MERCHANT_ID, {"amountUsd": "100.00", "transferKey": "q1-nov-u1"})
    assert result.transfer.amountVes == "21540.00" and result.transfer.rate == "215.4000"
    assert result.pendingVes == "21540.00"
    assert server.requests[0].path == f"/v1/merchants/{MERCHANT_ID}/transfers"
    assert server.requests[0].body == {"amountUsd": "100.00", "transferKey": "q1-nov-u1"}

    ids = [mv.id for mv in client.merchants.list_transactions(MERCHANT_ID, {"limit": 2})]
    assert ids == ["m1", "m2", "m3"]
    assert server.requests[1].path == f"/v1/merchants/{MERCHANT_ID}/transactions?limit=2"
    assert server.requests[2].path == f"/v1/merchants/{MERCHANT_ID}/transactions?limit=2&cursor=c2"

    statement = client.merchants.retrieve_statement(MERCHANT_ID, {"month": "2026-11"})
    assert statement.closingVes == "21540.00" and len(statement.movements) == 1
    assert server.requests[3].path == f"/v1/merchants/{MERCHANT_ID}/statement?month=2026-11&format=json"

    assert client.merchants.retrieve_statement_csv(MERCHANT_ID, {"month": "2026-11"}) == STATEMENT_CSV
    assert server.requests[4].path == f"/v1/merchants/{MERCHANT_ID}/statement?month=2026-11&format=csv"


async def test_async_merchant_transactions_and_statement(server: MockServer) -> None:
    server.script([
        Scripted(200, {"items": [_movement("m1")], "nextCursor": None}),
        Scripted(200, STATEMENT),
        Scripted(200, STATEMENT_CSV),
    ])
    async with AsyncVexPay("k", base_url=server.url) as client:
        assert [mv.id async for mv in client.merchants.list_transactions(MERCHANT_ID)] == ["m1"]
        assert (await client.merchants.retrieve_statement(MERCHANT_ID, {"month": "2026-11"})).openingVes == "0.00"
        assert await client.merchants.retrieve_statement_csv(MERCHANT_ID, {"month": "2026-11"}) == STATEMENT_CSV


TOPUP = {
    "id": "tp_1", "status": "pending", "amountVes": "100000.00", "amountUsd": "500.00", "bcvRate": "200.0000",
    "feePercent": "3.5000", "feeFixedUsd": "0.25", "feeVes": None, "creditedVes": None,
    "sourceNote": "Ingresos publicidad quincena 2", "payerPhone": "04121234567", "bankReference": None,
    "expiresAt": "2026-10-28T00:15:00.000Z", "completedAt": None, "availableAt": None, "heldVes": "0.00",
    "instantFeePercent": "1.5000", "instantFeeVes": "0.00", "instantReleasedAt": None,
    "receiver": {"bankCode": "0169", "phone": "04140000000", "identification": "J-000000000"},
    "test": True, "createdAt": "2026-10-28T00:00:00.000Z",
}
TOPUP_COMPLETED = {
    **TOPUP, "status": "completed", "feeVes": "3550.00", "creditedVes": "96450.00", "bankReference": "123456",
    "completedAt": "2026-10-28T00:05:00.000Z", "availableAt": "2026-10-29T00:05:00.000Z", "heldVes": "96450.00",
    "instantFeeVes": "1446.75", "receiver": None,
}
TOPUP_LIST = {"data": [TOPUP], "monthlyCapUsd": "3000.00", "monthUsedUsd": "500.00", "monthRemainingUsd": "2500.00"}
CREATE_TOPUP = {
    "amountVes": "100000.00", "payerPhone": "04121234567", "payerCedula": "V12345678",
    "sourceNote": "Ingresos publicidad quincena 2",
}


def test_balance_topups(server: MockServer) -> None:
    released = {**TOPUP_COMPLETED, "heldVes": "0.00", "availableAt": None, "instantReleasedAt": "2026-10-28T00:06:00.000Z"}
    server.script([
        Scripted(201, TOPUP),
        Scripted(200, TOPUP_LIST),
        Scripted(200, TOPUP),
        Scripted(200, TOPUP_COMPLETED),
        Scripted(200, released),
    ])
    client = VexPay("k", base_url=server.url)
    created = client.balance.topups.create(CREATE_TOPUP, idempotency_key="tp-1")
    assert created.receiver is not None and created.receiver.bankCode == "0169"
    assert (server.requests[0].method, server.requests[0].path) == ("POST", "/v1/balance/topups")
    assert server.requests[0].headers["idempotency-key"] == "tp-1"
    assert server.requests[0].body == CREATE_TOPUP

    listed = client.balance.topups.list({"limit": 5})
    assert [t.id for t in listed.data] == ["tp_1"] and listed.monthRemainingUsd == "2500.00"
    assert server.requests[1].path == "/v1/balance/topups?limit=5"

    assert client.balance.topups.retrieve("tp_1").id == "tp_1"
    assert (server.requests[2].method, server.requests[2].path) == ("GET", "/v1/balance/topups/tp_1")
    assert client.balance.topups.simulate("tp_1").status == "completed"
    assert (server.requests[3].method, server.requests[3].path) == ("POST", "/v1/balance/topups/tp_1/simulate")
    assert client.balance.topups.instant("tp_1").heldVes == "0.00"
    assert (server.requests[4].method, server.requests[4].path) == ("POST", "/v1/balance/topups/tp_1/instant")


def test_balance_topup_errors(server: MockServer) -> None:
    server.script([
        Scripted(409, {"error": "not_held", "message": "Nothing held"}),
        Scripted(422, {
            "error": "topup_cap_exceeded", "message": "Over the monthly limit",
            "capUsd": "3000.00", "usedUsd": "500.00", "remainingUsd": "2500.00", "remainingVes": "500000.00",
        }),
    ])
    client = VexPay("k", base_url=server.url, max_network_retries=0)
    with pytest.raises(ConflictError) as conflict:
        client.balance.topups.instant("tp_2")
    assert conflict.value.code == "not_held"
    with pytest.raises(InvalidRequestError) as capped:
        client.balance.topups.create({**CREATE_TOPUP, "amountVes": "999999999.00"})
    assert capped.value.code == "topup_cap_exceeded" and capped.value.status == 422
    assert capped.value.body["remainingVes"] == "500000.00"


async def test_async_balance_topups(server: MockServer) -> None:
    server.script([Scripted(201, TOPUP), Scripted(200, TOPUP_LIST), Scripted(200, TOPUP_COMPLETED)])
    async with AsyncVexPay("k", base_url=server.url) as client:
        assert (await client.balance.topups.create(CREATE_TOPUP)).status == "pending"
        assert (await client.balance.topups.list()).monthlyCapUsd == "3000.00"
        assert server.requests[1].path == "/v1/balance/topups"
        assert (await client.balance.topups.instant("tp_1")).creditedVes == "96450.00"
        assert server.requests[2].path == "/v1/balance/topups/tp_1/instant"
