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
