# Changelog

## 0.6.0

- Add `cop` (sync and async) — Colombian pesos through Bre-B, Nequi and Daviplata: `cop.payments.create()`, `retrieve()`, `submit_otp()`, `cancel()`, `refund()` and `cop.balance.retrieve()`. COP must be enabled on your account.

## 0.5.0

- Checkout sessions accept `"methods": ["cop"]`: Colombian pesos through Bre-B, Nequi and Daviplata on the hosted checkout, priced from `amountUsd` at VEX Pay's USDT/COP rate. `cop` is offered by default when COP is enabled on your account. COP payment reads and `payment.*` webhooks for checkout payments add `amountUsd` and `copRate`.

## 0.4.0

- Add `balance.transactions.list()` (sync and async): every movement in your VES balance (payments, fees, payouts, reversals, card chargebacks, adjustments, seller transfers, conversions), newest first and auto-paginating. The amounts sum to `ledgerNetVes` from `balance.retrieve()`, so your ledger can reconcile automatically.
- New webhook events `payment.chargeback` and `payment.chargeback_closed` for bank chargebacks on card payments, with `ledgerEntryIds` matching `balance.transactions`. `payment.reversed` adds `reversalType` (`reversal` | `chargeback`); the balance adds `chargebackFeesVes`.

## 0.3.0

- Add `conversions` (sync and async) to turn available VES into your USDT balance: `conversions.quotes.create()` locks a rate for 60 seconds (`sourceAmountVes` or `targetAmountUsdt`), `conversions.create({"quoteId": ...})` debits the VES and returns a `PENDING` conversion, plus `conversions.retrieve()`, `conversions.list()` (auto-paginating) and `conversions.cancel()`. New webhook events `conversion.completed` and `conversion.canceled`; the VES balance adds `convertedVes`. Conversions are enabled per account (403 `conversions_not_enabled` otherwise).
- Add USDC (Polygon and Base) to `crypto` (sync and async): `crypto.balance.retrieve()`, `crypto.deposit_addresses.create()`, `crypto.networks.list()` and `crypto.payouts.create()` accept `"currency": "USDT" | "USDC"` (default USDT, so existing calls are unchanged). New `crypto.balances.list()` returns every stablecoin balance.
- Payouts take `amount` (`amountUsdt` stays as a USDT-only alias). Crypto responses and `payment.completed` / `payout.*` events add `currency`, `amount` and `fee` for both coins. Checkout sessions accept `"methods": ["usdc"]`.

## 0.2.1

- `merchants.update()` (sync and async) accepts `applicationFeePercent` to set a merchant's negotiated marketplace commission (`None` returns the merchant to the tenant's default commission), and merchant responses include it. Charges that pass `merchantId` without `applicationFeeVes` / `applicationFeePercent` now apply that commission.

## 0.2.0

- Add `crypto` for USDT (sync and async): `crypto.balance.retrieve()`, `crypto.deposit_addresses.create()`, `crypto.networks.list()`, `crypto.payouts.create()` / `retrieve()`. USDT settles in USDT in its own balance; the calls raise `method_not_allowed` (403) when USDT isn't enabled on the account.
- Checkout sessions accept `"methods": ["usdt"]`; USDT `payment.completed` events add `amountUsdt`, `feeUsdt`, `network`, `txHashes`, `customerRef`, `underpaid` and `checkoutSession`.

## 0.1.1

- Add `payments.pago_movil.receiving_account()` (sync and async) for `GET /v1/payments/pago-movil/receiving-account`: the Pago Móvil account your customers pay into (bank, phone, identification), resolved with the same routing as `verify`, plus `configured` / `missing`.

## 0.1.0

- First release: sync `VexPay` and async `AsyncVexPay` clients, typed models, automatic `Idempotency-Key` and retries, auto-pagination, and webhook verification (`Webhook.construct_event`).
