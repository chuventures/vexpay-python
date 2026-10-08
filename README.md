# VEXPay Python SDK

The official Python library for the [VEXPay](https://vexwallet.co/vexpay) API: accept Venezuelan payments (Pago Móvil C2P, cards, débito inmediato), pay out to merchants, create checkout sessions, and verify signed webhooks.

- Sync (`VexPay`) and async (`AsyncVexPay`) clients with the same methods
- Typed Pydantic v2 models generated from the VEXPay OpenAPI contract
- Safe retries: every `POST` carries an `Idempotency-Key`, so a retried charge never charges twice
- Auto-pagination
- Webhook signature verification with replay protection
- Python 3.9+

## Install

```sh
pip install vexpay
```

## Quickstart

```python
from vexpay import VexPay

vexpay = VexPay()  # reads VEXPAY_API_KEY from the environment

quote = vexpay.quotes.retrieve({"usdAmount": 25})
print(f"$25 = Bs {quote.vesAmount} at BCV {quote.bcvRate}")
```

Keep your API key on the server. Use your test-mode key while you build; it runs against the sandbox provider. Request bodies and query parameters use the API's field names (`usdAmount`, `debtorBankCode`, …) — pass a `dict` or one of the models in `vexpay._generated.models`.

## Collect a Pago Móvil C2P payment

C2P is two steps: create an intent (the payer's bank sends them a token by SMS), then charge with the token your customer types in.

```python
from vexpay import VexPay

vexpay = VexPay()

payer = {
    "usdAmount": 25,
    "debtorId": "V12345678",
    "debtorCellPhone": "584141234567",
    "debtorBankCode": 102,
}

intent = vexpay.payments.c2p.request({**payer, "externalRef": "order-1042"})

token = input("Bank token: ")  # the customer reads it from their bank SMS

payment = vexpay.payments.c2p.execute({**payer, "intentId": intent.intentId, "token": token})
print(payment.paymentId, payment.status)  # "COMPLETED" or "PENDING" — confirm with the payment.* webhook
```

## Checkout sessions (hosted or embedded)

Let VEXPay collect the payment details. Redirect the buyer to `url`, or embed the checkout on your own site with [`@vexpay/js`](https://www.npmjs.com/package/@vexpay/js) and the one-time `clientSecret`.

```python
from vexpay import VexPay

vexpay = VexPay()

session = vexpay.checkout.sessions.create(
    {
        "amountUsd": 25,
        "reference": "order-1042",
        "description": "Pedido #1042",
        "successUrl": "https://shop.example/gracias",
        "metadata": {"orderId": "1042"},
    }
)
print(session.url)  # redirect here, or send session.clientSecret to the browser (never log or store it)

# Later — fulfil only after checking on the server:
current = vexpay.checkout.sessions.retrieve(session.id)
if current.status == "paid":
    print("ship order 1042")
```

The hosted page lets the buyer pick the currency — bolívares, stablecoins or Colombian pesos — and offers every method your account accepts. Limit it with `methods` (`c2p`, `vpos`, `usdt`, `usdc`, `cop`).

## USDT

USDT settles in USDT, into your VEXPay USDT balance (never converted to VES). It must be enabled on your account — otherwise these calls fail with `method_not_allowed` (403). Pay-ins cost 2.5 % + 0.50 USDT; payouts cost the network fee listed by `crypto.networks.list()`.

```python
from vexpay import VexPay, VexPayError

vexpay = VexPay()

try:
    networks = vexpay.crypto.networks.list({"amountUsdt": "50.00"})
except VexPayError as err:
    if err.code != "method_not_allowed":
        raise
    networks = []  # USDT isn't enabled on this account

if any(n.receiveEnabled for n in networks):
    # Hosted USDT checkout: the buyer picks a network and gets a deposit address.
    session = vexpay.checkout.sessions.create(
        {
            "amountUsd": 25,
            "reference": "order-1042",
            "methods": ["usdt"],
            "successUrl": "https://shop.example/gracias",
        }
    )
    print(session.url)
    print(vexpay.crypto.balance.retrieve())
```

Static deposit addresses (`crypto.deposit_addresses.create({"customerRef": "user_123", "network": "BEP20"})`) fire `payment.completed` with that `customerRef` on every deposit. Payouts (`crypto.payouts.create({... "idempotencyKey": "withdrawal-981"})`) debit amount + network fee and end in `payout.completed` (with `txHash`) or `payout.failed` (refunded). USDT `payment.completed` events add `amountUsdt`, `feeUsdt`, `network`, `txHashes` and `checkoutSession.reference`. **Don't fulfil when `underpaid` is `True`.**

### USDC

USDC (Polygon and Base) uses the same calls with `"currency": "USDC"`, has its own balance and must be enabled on your account separately. Without `currency`, every call stays in USDT.

```python
usdc = vexpay.crypto.balance.retrieve({"currency": "USDC"})
balances = vexpay.crypto.balances.list()  # USDT and USDC

vexpay.crypto.payouts.create(
    {
        "currency": "USDC",
        "network": "BASE",
        "address": "0x…",
        "amount": "50.00",
        "idempotencyKey": "withdrawal-982",
    }
)
```

Responses and events include `currency`, `amount` and `fee` for both coins (`amountUsdt` / `feeUsdt` stay on USDT only). Credit your customer in the `currency` the webhook reports.

## Convert VES to USDT

Turn available VES into your USDT balance. A quote locks the rate (market USDT/VES rate plus your spread) for 60 seconds; accepting it debits the VES at once and returns a `PENDING` conversion. VEXPay then delivers the USDT and sends `conversion.completed` (or `conversion.canceled`, with the VES returned). Conversions are on for every account that has USDT enabled — otherwise the calls fail with `conversions_not_enabled` (403). In test mode they complete immediately.

```python
quote = vexpay.conversions.quotes.create({"sourceAmountVes": "10000.00"})  # or {"targetAmountUsdt": "50.00"}
print(quote.rate, quote.targetAmountUsdt, quote.expiresAt)

conversion = vexpay.conversions.create(
    {"quoteId": quote.id, "reference": "treasury-2026-10-03"},
    idempotency_key="convert-2026-10-03",
)

for c in vexpay.conversions.list({"status": "PENDING"}):
    print(c.id, c.sourceAmountVes, "→", c.targetAmountUsdt)
vexpay.conversions.cancel(conversion.id)  # only while PENDING
```

## Colombian pesos (COP)

Collect pesos from buyers in Colombia through Bre-B, Nequi or Daviplata. Amounts are whole pesos, payments complete asynchronously (`payment.completed` / `payment.failed`), and completed payments go to your COP balance net of the COP fee. COP must be enabled on your account — otherwise the calls fail with `method_not_allowed` (403).

```python
from vexpay import VexPay

vexpay = VexPay()

# Bre-B: no buyer data. Show next.qrPngBase64 as an image and next.transferKey as text.
breb = vexpay.cop.payments.create(
    {"amountCop": 100000, "channel": "breb", "reference": "order-1042"},
    idempotency_key="order-1042-cop",
)

buyer = {"email": "juan@example.com", "phone": "3001234567", "documentType": "CC", "documentNumber": "1234567890"}

# Nequi: the buyer approves a push in the Nequi app.
vexpay.cop.payments.create({"amountCop": 50000, "channel": "nequi", "buyer": buyer})

# Daviplata: the buyer reads you the SMS code; submit it.
davi = vexpay.cop.payments.create({"amountCop": 50000, "channel": "daviplata", "buyer": buyer})
vexpay.cop.payments.submit_otp(davi.id, {"otp": "123456"})

status = vexpay.cop.payments.retrieve(breb.id).status  # pending | completed | failed | canceled | refunded
available = vexpay.cop.balance.retrieve().availableCop
```

`cancel(id)` cancels a pending payment and `refund(id)` refunds a completed one in full within 96 hours. A webhook for a COP payment has `data["method"] == "COP"`, with `channel`, `amountCop` and lowercase `status`.

**Test mode** (test API keys use a sandbox):

| Channel | What to use | Result |
|---|---|---|
| Bre-B | No buyer data | QR and key from the sandbox. **Never send real money to them** — sandbox keys are reachable from real banks and the money is not credited. |
| Nequi | Any valid data, e.g. phone `3001234567`, `CC` `1234567890`, any email | Completes on its own within about a minute |
| Daviplata | Same buyer data (`CC`, `CE` or `TI` only) | OTP `123456`, `000000` or `111111` completes it; any other code fails with `invalid_otp` |

## Webhooks

VEXPay signs every delivery with a `VexPay-Signature` header. Verify it with the **raw** request body — parsing and re-serializing JSON changes the bytes and breaks the signature (Flask: `request.get_data()`, Django: `request.body`, FastAPI: `await request.body()`).

```python
import os
from typing import Optional

from vexpay import PaymentEvent, SignatureVerificationError, Webhook


def handle_webhook(raw_body: bytes, signature: Optional[str]) -> int:
    """Framework-agnostic handler: returns the HTTP status to answer with."""
    try:
        event = Webhook.construct_event(raw_body, signature, os.environ["VEXPAY_WEBHOOK_SECRET"])
    except SignatureVerificationError:
        return 400

    if isinstance(event, PaymentEvent) and event.event == "payment.completed":
        data = event.data
        reference = data.externalRef or (data.checkoutSession.reference if data.checkoutSession else None)
        print("paid", data.paymentId, reference)
    return 204
```

Deliveries older than 5 minutes are rejected as possible replays; pass `tolerance=` (seconds) to change that. Each delivery also carries a `VexPay-Event-Id` header you can use to deduplicate. In your own tests, sign fixtures with `Webhook.generate_test_header(payload, secret)`.

## Errors

Every error extends `VexPayError` and carries `status`, the API `code` (e.g. `insufficient_balance`), and the response `body`.

```python
from vexpay import ConflictError, InvalidRequestError, NotFoundError, VexPay, VexPayError

vexpay = VexPay()

try:
    vexpay.payouts.create(
        {
            "merchantId": "4f0c6f1e-2b7d-4c1a-9e3f-5a6b7c8d9e0f",
            "monto": "1523.40",
            "concepto": "Liquidación semana 30",
            "externalRef": "po_2026_30_maria",
        }
    )
except InvalidRequestError as error:
    print("fix the request:", error.code, error.message)
except NotFoundError:
    print("no such merchant")
except ConflictError as error:
    print("externalRef reused with a different payload", error.body)
except VexPayError as error:
    print(error.status, error.code, error.message)
```

| Class | When |
|---|---|
| `AuthenticationError` | 401 — missing or invalid API key |
| `InvalidRequestError` | 400, 403, 410, 422 — fix the request |
| `NotFoundError` | 404 |
| `ConflictError` | 409 — e.g. `external_ref_conflict`, `idempotency_key_reused` |
| `RateLimitError` | 429, after retries |
| `APIError` | 5xx, after retries |
| `APIConnectionError` / `APITimeoutError` | no HTTP answer, after retries |
| `SignatureVerificationError` | a webhook did not verify |

## Retries and idempotency

The SDK retries connection errors, timeouts, `429`, `5xx`, and `409 idempotency_request_in_progress` up to `max_network_retries` times (default 2) with exponential backoff, honouring `Retry-After`. Every `POST` gets a random `Idempotency-Key` that stays the same across its retries. Supply your own to make retries safe across process restarts too:

```python
from vexpay import VexPay

vexpay = VexPay(max_network_retries=3, timeout=20.0)

quote = vexpay.quotes.retrieve({"usdAmount": 10}, timeout=5.0)
session = vexpay.checkout.sessions.create(
    {"amountUsd": 10, "reference": "order-1043"},
    idempotency_key="order-1043-session",
)
print(quote.vesAmount, session.id)
```

## Pagination

`list()` on payouts, merchants, and products returns the first page; iterate it to walk every item across pages:

```python
from vexpay import VexPay

vexpay = VexPay()

page = vexpay.merchants.list({"limit": 100})
print(len(page.items), page.next_cursor)

for merchant in vexpay.merchants.list({"status": "verified", "isActive": "true"}):
    print(merchant.merchantId, merchant.name)

recent = vexpay.payouts.list({"limit": 50}).to_list(limit=200)
print(len(recent))
```

## Async

`AsyncVexPay` has the same resources; await the calls, and use `async for` to paginate:

```python
import asyncio

from vexpay import AsyncVexPay


async def main() -> None:
    async with AsyncVexPay() as vexpay:
        banks = await vexpay.banks.list()
        print(len(banks), "banks")

        first_page = await vexpay.products.list({"limit": 10})
        print(len(first_page.items))

        async for payout in vexpay.payouts.list():
            print(payout.payoutId, payout.status)


asyncio.run(main())
```

## Configuration

```python
from vexpay import VexPay

with VexPay(
    api_key="sk_test_…",               # default: VEXPAY_API_KEY env var
    base_url="http://localhost:3010",  # default: https://api.pay.vexwallet.co
    timeout=30.0,
    max_network_retries=2,
) as vexpay:
    print(len(vexpay.banks.list()), "banks")
```

Pass `http_client=httpx.Client(...)` (or `httpx.AsyncClient`) to control proxies, connection pooling, or instrumentation.

## Resources

| Namespace | Methods |
|---|---|
| `banks` | `list` |
| `quotes` | `retrieve` |
| `balance` | `retrieve` |
| `balance.transactions` | `list` (auto-paginating; every movement in your VES balance — reconcile with `ledgerNetVes`) |
| `payments` | `retrieve`, `retrieve_by_ref`, `reverse` |
| `payments.c2p` | `request`, `execute` |
| `payments.vpos` | `create` |
| `payments.pago_movil` | `verify` |
| `payments.debit` · `credit` · `operations` · `dispersals` · `change` | débito/crédito inmediato and disbursements (advanced payments) |
| `checkout.sessions` | `create`, `retrieve` |
| `crypto.balance` | `retrieve` |
| `crypto.balances` | `list` |
| `crypto.deposit_addresses` | `create` |
| `crypto.networks` | `list` |
| `crypto.payouts` | `create`, `retrieve` |
| `conversions` | `create`, `list`, `retrieve`, `cancel` |
| `conversions.quotes` | `create` |
| `cop.payments` | `create`, `retrieve`, `submit_otp`, `cancel`, `refund` |
| `cop.balance` | `retrieve` |
| `merchants` | `create`, `list`, `retrieve`, `retrieve_by_ref`, `update`, `delete`, `retrieve_balance`, `transfer`, `list_audit_events`, `start_verification`, `confirm_verification` |
| `merchants.payout_methods` | `list`, `create`, `set_default`, `delete`, `start_verification`, `confirm_verification` |
| `payouts` | `create`, `create_instant`, `create_batch`, `list`, `retrieve`, `retrieve_by_ref` |
| `products` | `create`, `list`, `retrieve`, `update`, `delete`, `create_link`, `list_links` |
| `payment_links` | `retrieve`, `update`, `delete` |
| `tenant_payout_account` | `retrieve`, `upsert`, `create`, `start_verification`, `confirm_verification` |
| `webhook_endpoints` | `create`, `list`, `update`, `delete`, `send_test` |
| `Webhook` / `client.webhooks` | `construct_event`, `generate_test_header` (offline) |

## License

MIT
