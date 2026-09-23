# Changelog

## 0.1.1

- Add `payments.pago_movil.receiving_account()` (sync and async) for `GET /v1/payments/pago-movil/receiving-account`: the Pago Móvil account your customers pay into (bank, phone, identification), resolved with the same routing as `verify`, plus `configured` / `missing`.

## 0.1.0

- First release: sync `VexPay` and async `AsyncVexPay` clients, typed models, automatic `Idempotency-Key` and retries, auto-pagination, and webhook verification (`Webhook.construct_event`).
