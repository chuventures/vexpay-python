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

from vexpay import AsyncPage, AsyncVexPay, InvalidRequestError, SyncPage, VexPay
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
PATH_ARG_NAMES = {"id", "merchant_id", "method_id", "external_ref"}


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
    for resource in ("merchants", "payouts", "products"):
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

