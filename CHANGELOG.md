# Changelog

## 0.2.1

- `merchants.update()` (sync and async) accepts `applicationFeePercent` to set a merchant's negotiated marketplace commission (`None` returns the merchant to the tenant's default commission), and merchant responses include it. Charges that pass `merchantId` without `applicationFeeVes` / `applicationFeePercent` now apply that commission.

## 0.2.0

- Add `crypto` for USDT (sync and async): `crypto.balance.retrieve()`, `crypto.deposit_addresses.create()`, `crypto.networks.list()`, `crypto.payouts.create()` / `retrieve()`. USDT settles in USDT in its own balance; the calls raise `method_not_allowed` (403) when USDT isn't enabled on the account.
- Checkout sessions accept `"methods": ["usdt"]`; USDT `payment.completed` events add `amountUsdt`, `feeUsdt`, `network`, `txHashes`, `customerRef`, `underpaid` and `checkoutSession`.

## 0.1.1

- Add `payments.pago_movil.receiving_account()` (sync and async) for `GET /v1/payments/pago-movil/receiving-account`: the Pago Móvil account your customers pay into (bank, phone, identification), resolved with the same routing as `verify`, plus `configured` / `missing`.

## 0.1.0

- First release: sync `VexPay` and async `AsyncVexPay` clients, typed models, automatic `Idempotency-Key` and retries, auto-pagination, and webhook verification (`Webhook.construct_event`).
