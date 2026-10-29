"""Asynchronous resources — generated from ``_resources.py`` by ``scripts/generate_async.py``. Do not edit."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional, Union

from typing_extensions import Unpack

from ._core import RequestOptions
from ._generated import models as m
from ._pagination import AsyncPage
from ._resource import AsyncAPIResource

Params = Mapping[str, Any]


# ── payments ──────────────────────────────────────────────────────────────────


class AsyncC2p(AsyncAPIResource):
    """Pago Móvil C2P: request the bank OTP, then charge with the customer's token."""

    async def request(
        self, params: Union[m.C2pRequestDto, Params], **options: Unpack[RequestOptions]
    ) -> m.C2pIntentResponseDto:
        return await self._request_model("Payments_requestC2p", m.C2pIntentResponseDto, body=params, options=options)

    async def execute(
        self, params: Union[m.C2pPaymentDto, Params], **options: Unpack[RequestOptions]
    ) -> m.PaymentReceiptDto:
        return await self._request_model("Payments_executeC2p", m.PaymentReceiptDto, body=params, options=options)


class AsyncVpos(AsyncAPIResource):
    """Card payments. Prefer the hosted/embedded checkout so card data never touches your servers."""

    async def create(
        self, params: Union[m.VposPaymentDto, Params], **options: Unpack[RequestOptions]
    ) -> m.PaymentReceiptDto:
        return await self._request_model("Payments_executeVpos", m.PaymentReceiptDto, body=params, options=options)


class AsyncPagoMovil(AsyncAPIResource):
    """Confirm a Pago Móvil the customer already sent to you."""

    async def receiving_account(self, **options: Unpack[RequestOptions]) -> m.PagoMovilReceivingAccountDto:
        """The account your customers must send the Pago Móvil to. Don't offer Pago Móvil while ``configured`` is false."""
        return await self._request_model(
            "Payments_getPagoMovilReceivingAccount", m.PagoMovilReceivingAccountDto, options=options
        )

    async def verify(
        self, params: Union[m.PagoMovilVerifyDto, Params], **options: Unpack[RequestOptions]
    ) -> m.PaymentReceiptDto:
        return await self._request_model("Payments_verifyPagoMovil", m.PaymentReceiptDto, body=params, options=options)


class AsyncDebit(AsyncAPIResource):
    """Débito inmediato (advanced payments, enabled per account)."""

    async def request_otp(
        self, params: Union[m.GenerateDebitOtpDto, Params], **options: Unpack[RequestOptions]
    ) -> m.DebitOtpResponseDto:
        return await self._request_model("R4Operations_generarOtp", m.DebitOtpResponseDto, body=params, options=options)

    async def execute(
        self, params: Union[m.ImmediateDebitDto, Params], **options: Unpack[RequestOptions]
    ) -> m.ImmediateDebitResponseDto:
        return await self._request_model(
            "R4Operations_debitoInmediato", m.ImmediateDebitResponseDto, body=params, options=options
        )


class AsyncCredit(AsyncAPIResource):
    """Crédito inmediato and disbursements (advanced payments, enabled per account)."""

    async def create(
        self, params: Union[m.ImmediateCreditDto, Params], **options: Unpack[RequestOptions]
    ) -> m.R4OperationResponseDto:
        return await self._request_model(
            "R4Operations_creditoInmediato", m.R4OperationResponseDto, body=params, options=options
        )

    async def to_account(
        self, params: Union[m.AccountCreditDto, Params], **options: Unpack[RequestOptions]
    ) -> m.R4OperationResponseDto:
        return await self._request_model(
            "R4Operations_creditoCuentas", m.R4OperationResponseDto, body=params, options=options
        )

    async def disburse(
        self, params: Union[m.CreditDisbursementDto, Params], **options: Unpack[RequestOptions]
    ) -> m.CreditDisbursementResponseDto:
        return await self._request_model(
            "R4Operations_dispersarCredito", m.CreditDisbursementResponseDto, body=params, options=options
        )


class AsyncOperations(AsyncAPIResource):
    """Bank operation status for débito/crédito (advanced payments, enabled per account)."""

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.R4OperationResponseDto:
        return await self._request_model(
            "R4Operations_consultarOperacion", m.R4OperationResponseDto, path={"id": id}, options=options
        )

    async def poll(
        self, params: Union[m.ManualOperationPollDto, Params], **options: Unpack[RequestOptions]
    ) -> m.ManualOperationPollResponseDto:
        return await self._request_model(
            "R4Operations_pollOperation", m.ManualOperationPollResponseDto, body=params, options=options
        )


class AsyncDispersals(AsyncAPIResource):
    """Account payout dispersion (advanced payments, enabled per account)."""

    async def create(
        self, params: Union[m.PayoutDto, Params], **options: Unpack[RequestOptions]
    ) -> m.AccountPayoutDispersionResponseDto:
        return await self._request_model(
            "R4Operations_dispersarPagos", m.AccountPayoutDispersionResponseDto, body=params, options=options
        )


class AsyncChange(AsyncAPIResource):
    """Vuelto / change payments (advanced payments, enabled per account)."""

    async def create(
        self, params: Union[m.ChangePaymentDto, Params], **options: Unpack[RequestOptions]
    ) -> m.ChangePaymentResponseDto:
        return await self._request_model(
            "R4Operations_ejecutarVuelto", m.ChangePaymentResponseDto, body=params, options=options
        )


class AsyncPayments(AsyncAPIResource):
    def __init__(self, http: Any) -> None:
        super().__init__(http)
        self.c2p = AsyncC2p(self._http)
        self.vpos = AsyncVpos(self._http)
        self.pago_movil = AsyncPagoMovil(self._http)
        self.debit = AsyncDebit(self._http)
        self.credit = AsyncCredit(self._http)
        self.operations = AsyncOperations(self._http)
        self.dispersals = AsyncDispersals(self._http)
        self.change = AsyncChange(self._http)

    async def methods(self, **options: Unpack[RequestOptions]) -> m.PaymentMethodsResponseDto:
        """Bolívar methods your account can take now (``pago_movil``, ``c2p``, ``vpos``), with a reason when unavailable."""
        return await self._request_model("Payments_listPaymentMethods", m.PaymentMethodsResponseDto, options=options)

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.PaymentReceiptDto:
        return await self._request_model("Payments_getPayment", m.PaymentReceiptDto, path={"id": id}, options=options)

    async def retrieve_by_ref(self, external_ref: str, **options: Unpack[RequestOptions]) -> m.PaymentReceiptDto:
        """Look up a payment by the ``externalRef`` you sent."""
        return await self._request_model(
            "Payments_getPaymentByRef", m.PaymentReceiptDto, path={"externalRef": external_ref}, options=options
        )

    async def reverse(self, id: str, **options: Unpack[RequestOptions]) -> m.PaymentReceiptDto:
        """Reverse a completed C2P payment."""
        return await self._request_model("Payments_reversePayment", m.PaymentReceiptDto, path={"id": id}, options=options)


# ── checkout ──────────────────────────────────────────────────────────────────


class AsyncCheckoutSessions(AsyncAPIResource):
    """Single-purchase checkouts: redirect to ``url``, or embed with @vexpay/js using ``clientSecret``."""

    async def create(
        self, params: Union[m.CreateCheckoutSessionDto, Params], **options: Unpack[RequestOptions]
    ) -> m.CheckoutSessionResponseDto:
        """``clientSecret`` is returned only here — hand it to the browser, never store or log it."""
        return await self._request_model(
            "CheckoutSessions_create", m.CheckoutSessionResponseDto, body=params, options=options
        )

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.CheckoutSessionResponseDto:
        return await self._request_model(
            "CheckoutSessions_retrieve", m.CheckoutSessionResponseDto, path={"id": id}, options=options
        )


class AsyncCheckout(AsyncAPIResource):
    def __init__(self, http: Any) -> None:
        super().__init__(http)
        self.sessions = AsyncCheckoutSessions(self._http)


# ── merchants ─────────────────────────────────────────────────────────────────


class AsyncPayoutMethods(AsyncAPIResource):
    """Where a merchant gets paid (bank account or Pago Móvil)."""

    async def list(self, merchant_id: str, **options: Unpack[RequestOptions]) -> m.PayoutMethodListResponseDto:
        return await self._request_model(
            "Merchants_listPayoutMethods", m.PayoutMethodListResponseDto, path={"id": merchant_id}, options=options
        )

    async def create(
        self,
        merchant_id: str,
        params: Union[m.CreatePayoutMethodDto, Params],
        **options: Unpack[RequestOptions],
    ) -> m.PayoutMethodResponseDto:
        return await self._request_model(
            "Merchants_addPayoutMethod",
            m.PayoutMethodResponseDto,
            path={"id": merchant_id},
            body=params,
            options=options,
        )

    async def set_default(
        self, merchant_id: str, method_id: str, **options: Unpack[RequestOptions]
    ) -> m.PayoutMethodResponseDto:
        return await self._request_model(
            "Merchants_setDefaultPayoutMethod",
            m.PayoutMethodResponseDto,
            path={"id": merchant_id, "methodId": method_id},
            options=options,
        )

    async def delete(self, merchant_id: str, method_id: str, **options: Unpack[RequestOptions]) -> None:
        return await self._request_none(
            "Merchants_deletePayoutMethod", path={"id": merchant_id, "methodId": method_id}, options=options
        )

    async def start_verification(
        self, merchant_id: str, method_id: str, **options: Unpack[RequestOptions]
    ) -> m.VerifyStartResponseDto:
        """Send micro-deposits to this payout method."""
        return await self._request_model(
            "Merchants_startVerifyMethod",
            m.VerifyStartResponseDto,
            path={"id": merchant_id, "methodId": method_id},
            options=options,
        )

    async def confirm_verification(
        self,
        merchant_id: str,
        method_id: str,
        params: Union[m.ConfirmMerchantVerifyDto, Params],
        **options: Unpack[RequestOptions],
    ) -> m.VerifyConfirmResponseDto:
        """Confirm the micro-deposit amounts the merchant saw."""
        return await self._request_model(
            "Merchants_confirmVerifyMethod",
            m.VerifyConfirmResponseDto,
            path={"id": merchant_id, "methodId": method_id},
            body=params,
            options=options,
        )


class AsyncMerchants(AsyncAPIResource):
    def __init__(self, http: Any) -> None:
        super().__init__(http)
        self.payout_methods = AsyncPayoutMethods(self._http)

    async def create(
        self, params: Union[m.CreateMerchantDto, Params], **options: Unpack[RequestOptions]
    ) -> m.MerchantResponseDto:
        """``externalRef`` is required and is the idempotency key for merchant creation."""
        return await self._request_model("Merchants_create", m.MerchantResponseDto, body=params, options=options)

    def list(
        self, params: Optional[Params] = None, **options: Unpack[RequestOptions]
    ) -> AsyncPage[m.MerchantListResponseDto, m.MerchantResponseDto]:
        """First page of merchants; iterate the result for every merchant."""
        query = {key: value for key, value in (params or {}).items() if key != "externalRef"}
        return AsyncPage(
            lambda cursor: self._request_model(
                "Merchants_listOrGetByRef",
                m.MerchantListResponseDto,
                query={**query, "cursor": cursor},
                options=options,
            ),
            query.get("cursor"),
        )

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.MerchantResponseDto:
        return await self._request_model("Merchants_getById", m.MerchantResponseDto, path={"id": id}, options=options)

    async def retrieve_by_ref(self, external_ref: str, **options: Unpack[RequestOptions]) -> m.MerchantResponseDto:
        """Look up a merchant by the ``externalRef`` you created it with."""
        return await self._request_model(
            "Merchants_listOrGetByRef", m.MerchantResponseDto, query={"externalRef": external_ref}, options=options
        )

    async def update(
        self, id: str, params: Union[m.UpdateMerchantDto, Params], **options: Unpack[RequestOptions]
    ) -> m.MerchantResponseDto:
        return await self._request_model(
            "Merchants_update", m.MerchantResponseDto, path={"id": id}, body=params, options=options
        )

    async def delete(self, id: str, **options: Unpack[RequestOptions]) -> m.DeleteMerchantResponseDto:
        return await self._request_model("Merchants_remove", m.DeleteMerchantResponseDto, path={"id": id}, options=options)

    async def retrieve_balance(self, id: str, **options: Unpack[RequestOptions]) -> m.MerchantBalanceDto:
        return await self._request_model("Merchants_getBalance", m.MerchantBalanceDto, path={"id": id}, options=options)

    async def transfer(
        self, id: str, params: Union[m.CreateMerchantTransferDto, Params], **options: Unpack[RequestOptions]
    ) -> m.MerchantTransferResponseDto:
        """Credit this seller's pending balance from your platform balance.

        Send ``amountVes``, or ``amountUsd`` to convert at the official BCV rate (503 ``rate_unavailable``
        when no rate can be read); ``transferKey`` makes it idempotent. Returns the seller balance plus
        ``transfer`` (the amounts and rate used)."""
        return await self._request_model(
            "Merchants_transfer", m.MerchantTransferResponseDto, path={"id": id}, body=params, options=options
        )

    def list_transactions(
        self, id: str, params: Optional[Params] = None, **options: Unpack[RequestOptions]
    ) -> AsyncPage[m.MerchantMovementListDto, m.MerchantMovementDto]:
        """Seller balance movements, newest first; iterate the result for every movement."""
        query = dict(params or {})
        return AsyncPage(
            lambda cursor: self._request_model(
                "Merchants_listTransactions",
                m.MerchantMovementListDto,
                path={"id": id},
                query={**query, "cursor": cursor},
                options=options,
            ),
            query.get("cursor"),
        )

    async def retrieve_statement(self, id: str, params: Params, **options: Unpack[RequestOptions]) -> m.MerchantStatementDto:
        """Monthly statement, e.g. ``{"month": "2026-11"}`` (America/Caracas): opening, movements, closing."""
        return await self._request_model(
            "Merchants_statement",
            m.MerchantStatementDto,
            path={"id": id},
            query={**params, "format": "json"},
            options=options,
        )

    async def retrieve_statement_csv(self, id: str, params: Params, **options: Unpack[RequestOptions]) -> str:
        """The same monthly statement as CSV (with a running balance column)."""
        body = await self._request_json(
            "Merchants_statement", path={"id": id}, query={**params, "format": "csv"}, options=options
        )
        return body if isinstance(body, str) else ""

    async def list_audit_events(self, id: str, **options: Unpack[RequestOptions]) -> m.MerchantAuditEventListDto:
        return await self._request_model(
            "Merchants_listAuditEvents", m.MerchantAuditEventListDto, path={"id": id}, options=options
        )

    async def start_verification(self, id: str, **options: Unpack[RequestOptions]) -> m.VerifyStartResponseDto:
        """Send micro-deposits to the merchant's default payout method."""
        return await self._request_model("Merchants_startVerify", m.VerifyStartResponseDto, path={"id": id}, options=options)

    async def confirm_verification(
        self, id: str, params: Union[m.ConfirmMerchantVerifyDto, Params], **options: Unpack[RequestOptions]
    ) -> m.VerifyConfirmResponseDto:
        return await self._request_model(
            "Merchants_confirmVerify", m.VerifyConfirmResponseDto, path={"id": id}, body=params, options=options
        )


# ── payouts, products, links ──────────────────────────────────────────────────


class AsyncPayouts(AsyncAPIResource):
    """VES payouts to verified merchants. ``externalRef`` is the idempotency key."""

    async def create(
        self, params: Union[m.CreatePayoutDto, Params], **options: Unpack[RequestOptions]
    ) -> m.PayoutResponseDto:
        return await self._request_model("Payouts_create", m.PayoutResponseDto, body=params, options=options)

    async def create_instant(
        self, params: Union[m.CreateInstantPayoutDto, Params], **options: Unpack[RequestOptions]
    ) -> m.PayoutResponseDto:
        return await self._request_model("Payouts_createInstant", m.PayoutResponseDto, body=params, options=options)

    async def create_batch(
        self, params: Union[m.CreatePayoutBatchDto, Params], **options: Unpack[RequestOptions]
    ) -> m.PayoutBatchResponseDto:
        return await self._request_model("Payouts_createBatch", m.PayoutBatchResponseDto, body=params, options=options)

    def list(
        self, params: Optional[Params] = None, **options: Unpack[RequestOptions]
    ) -> AsyncPage[m.PayoutListResponseDto, m.PayoutResponseDto]:
        query = dict(params or {})
        return AsyncPage(
            lambda cursor: self._request_model(
                "Payouts_list", m.PayoutListResponseDto, query={**query, "cursor": cursor}, options=options
            ),
            query.get("cursor"),
        )

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.PayoutResponseDto:
        return await self._request_model("Payouts_getById", m.PayoutResponseDto, path={"id": id}, options=options)

    async def retrieve_by_ref(self, external_ref: str, **options: Unpack[RequestOptions]) -> m.PayoutResponseDto:
        return await self._request_model(
            "Payouts_getByRef", m.PayoutResponseDto, path={"externalRef": external_ref}, options=options
        )


class AsyncProducts(AsyncAPIResource):
    """No-code products sold through hosted payment links."""

    async def create(
        self, params: Union[m.CreateProductDto, Params], **options: Unpack[RequestOptions]
    ) -> m.ProductResponseDto:
        return await self._request_model("Products_create", m.ProductResponseDto, body=params, options=options)

    def list(
        self, params: Optional[Params] = None, **options: Unpack[RequestOptions]
    ) -> AsyncPage[m.ProductListResponseDto, m.ProductResponseDto]:
        query = dict(params or {})
        return AsyncPage(
            lambda cursor: self._request_model(
                "Products_list", m.ProductListResponseDto, query={**query, "cursor": cursor}, options=options
            ),
            query.get("cursor"),
        )

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.ProductResponseDto:
        return await self._request_model("Products_get", m.ProductResponseDto, path={"id": id}, options=options)

    async def update(
        self, id: str, params: Union[m.UpdateProductDto, Params], **options: Unpack[RequestOptions]
    ) -> m.ProductResponseDto:
        return await self._request_model(
            "Products_update", m.ProductResponseDto, path={"id": id}, body=params, options=options
        )

    async def delete(self, id: str, **options: Unpack[RequestOptions]) -> None:
        return await self._request_none("Products_remove", path={"id": id}, options=options)

    async def create_link(
        self, id: str, params: Union[m.CreatePaymentLinkDto, Params], **options: Unpack[RequestOptions]
    ) -> m.PaymentLinkResponseDto:
        """Publish a shareable ``/pay/:slug`` link for this product."""
        return await self._request_model(
            "Products_createLink", m.PaymentLinkResponseDto, path={"id": id}, body=params, options=options
        )

    async def list_links(self, id: str, **options: Unpack[RequestOptions]) -> m.PaymentLinkListResponseDto:
        return await self._request_model(
            "Products_listLinks", m.PaymentLinkListResponseDto, path={"id": id}, options=options
        )


class AsyncPaymentLinks(AsyncAPIResource):
    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.PaymentLinkResponseDto:
        return await self._request_model("PaymentLinks_get", m.PaymentLinkResponseDto, path={"id": id}, options=options)

    async def update(
        self, id: str, params: Union[m.UpdatePaymentLinkDto, Params], **options: Unpack[RequestOptions]
    ) -> m.PaymentLinkResponseDto:
        return await self._request_model(
            "PaymentLinks_update", m.PaymentLinkResponseDto, path={"id": id}, body=params, options=options
        )

    async def delete(self, id: str, **options: Unpack[RequestOptions]) -> None:
        return await self._request_none("PaymentLinks_remove", path={"id": id}, options=options)


# ── account ───────────────────────────────────────────────────────────────────


class AsyncBanks(AsyncAPIResource):
    """Venezuelan bank catalog (SIMF codes, supported services, logos)."""

    async def list(self, **options: Unpack[RequestOptions]) -> list[m.BankResponseDto]:
        raw = await self._request_json("Payments_getBanks", options=options)
        return [m.BankResponseDto.model_validate(bank) for bank in raw]


class AsyncQuotes(AsyncAPIResource):
    """USD → VES at the official BCV rate."""

    async def retrieve(self, params: Params, **options: Unpack[RequestOptions]) -> m.QuoteResponseDto:
        return await self._request_model("Payments_getQuote", m.QuoteResponseDto, query=params, options=options)


class AsyncBalanceTransactions(AsyncAPIResource):
    """Every movement in your VES balance, newest first. The amounts sum to ``ledger_net_ves``."""

    def list(
        self, params: Optional[Params] = None, **options: Unpack[RequestOptions]
    ) -> AsyncPage[m.BalanceTransactionListDto, m.BalanceTransactionDto]:
        query = dict(params or {})
        return AsyncPage(
            lambda cursor: self._request_model(
                "Balance_listTransactions", m.BalanceTransactionListDto, query={**query, "cursor": cursor}, options=options
            ),
            query.get("cursor"),
        )


class AsyncBalanceTopups(AsyncAPIResource):
    """Load your own Bs balance by Pago Móvil (money that is not a sale). Enabled per account.

    Send the exact ``amountVes`` from ``payerPhone`` to the returned ``receiver`` before ``expiresAt``; the
    top-up completes when the transfer arrives. Each top-up needs a ``sourceNote`` and counts against your
    monthly limit (``topup_cap_exceeded``, 422).
    """

    async def create(self, params: Union[m.CreateTopupDto, Params], **options: Unpack[RequestOptions]) -> m.TopupDto:
        return await self._request_model("Topups_create", m.TopupDto, body=params, options=options)

    async def list(self, params: Optional[Params] = None, **options: Unpack[RequestOptions]) -> m.TopupListDto:
        """Your latest top-ups (newest first, ``limit`` 1–100) plus this month's limit usage."""
        return await self._request_model("Topups_list", m.TopupListDto, query=params or {}, options=options)

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.TopupDto:
        return await self._request_model("Topups_get", m.TopupDto, path={"id": id}, options=options)

    async def instant(self, id: str, **options: Unpack[RequestOptions]) -> m.TopupDto:
        """Release the still-held part of a completed top-up now, for ``instantFeeVes``. Idempotent;
        ``not_held`` (409) when nothing is held."""
        return await self._request_model("Topups_instant", m.TopupDto, path={"id": id}, options=options)

    async def simulate(self, id: str, **options: Unpack[RequestOptions]) -> m.TopupDto:
        """Test mode only: complete the top-up as if the Pago Móvil arrived."""
        return await self._request_model("Topups_simulate", m.TopupDto, path={"id": id}, options=options)


class AsyncBalance(AsyncAPIResource):
    def __init__(self, http: Any) -> None:
        super().__init__(http)
        self.transactions = AsyncBalanceTransactions(self._http)
        self.topups = AsyncBalanceTopups(self._http)

    async def retrieve(self, **options: Unpack[RequestOptions]) -> m.PlatformBalanceDto:
        return await self._request_model("Balance_getBalance", m.PlatformBalanceDto, options=options)


class AsyncTenantPayoutAccount(AsyncAPIResource):
    """The account your own VEXPay earnings are paid out to."""

    async def retrieve(self, **options: Unpack[RequestOptions]) -> m.TenantPayoutAccountResponseDto:
        return await self._request_model("TenantPayoutAccount_get", m.TenantPayoutAccountResponseDto, options=options)

    async def upsert(
        self, params: Union[m.UpsertTenantPayoutAccountDto, Params], **options: Unpack[RequestOptions]
    ) -> m.TenantPayoutAccountResponseDto:
        """Create or replace the payout account (PUT)."""
        return await self._request_model(
            "TenantPayoutAccount_upsert", m.TenantPayoutAccountResponseDto, body=params, options=options
        )

    async def create(
        self, params: Union[m.UpsertTenantPayoutAccountDto, Params], **options: Unpack[RequestOptions]
    ) -> m.TenantPayoutAccountResponseDto:
        """Same as ``upsert``, sent as POST (supports ``Idempotency-Key``)."""
        return await self._request_model(
            "TenantPayoutAccount_upsertPost", m.TenantPayoutAccountResponseDto, body=params, options=options
        )

    async def start_verification(self, **options: Unpack[RequestOptions]) -> m.TenantPayoutAccountVerifyStartResponseDto:
        return await self._request_model(
            "TenantPayoutAccount_startVerify", m.TenantPayoutAccountVerifyStartResponseDto, options=options
        )

    async def confirm_verification(
        self, params: Union[m.ConfirmTenantPayoutAccountVerifyDto, Params], **options: Unpack[RequestOptions]
    ) -> m.TenantPayoutAccountVerifyConfirmResponseDto:
        return await self._request_model(
            "TenantPayoutAccount_confirmVerify",
            m.TenantPayoutAccountVerifyConfirmResponseDto,
            body=params,
            options=options,
        )


class AsyncWebhookEndpoints(AsyncAPIResource):
    """Where VEXPay delivers signed webhooks."""

    async def create(
        self, params: Union[m.CreateWebhookDto, Params], **options: Unpack[RequestOptions]
    ) -> m.WebhookEndpointDto:
        """The response includes the signing ``secret`` — store it to verify deliveries."""
        return await self._request_model("Webhooks_createWebhook", m.WebhookEndpointDto, body=params, options=options)

    async def list(self, **options: Unpack[RequestOptions]) -> list[m.WebhookEndpointDto]:
        raw = await self._request_json("Webhooks_listWebhooks", options=options)
        return [m.WebhookEndpointDto.model_validate(endpoint) for endpoint in raw]

    async def update(
        self, id: str, params: Union[m.UpdateWebhookDto, Params], **options: Unpack[RequestOptions]
    ) -> m.WebhookEndpointDto:
        return await self._request_model(
            "Webhooks_updateWebhook", m.WebhookEndpointDto, path={"id": id}, body=params, options=options
        )

    async def delete(self, id: str, **options: Unpack[RequestOptions]) -> m.DeleteWebhookResponseDto:
        return await self._request_model(
            "Webhooks_deleteWebhook", m.DeleteWebhookResponseDto, path={"id": id}, options=options
        )

    async def send_test(self, **options: Unpack[RequestOptions]) -> m.NotificationTestResponseDto:
        """Send a ``notification.test`` delivery to your endpoints."""
        return await self._request_model("Notifications_sendTest", m.NotificationTestResponseDto, options=options)


# ── crypto (USDT, USDC) ───────────────────────────────────────────────────────


class AsyncCryptoBalance(AsyncAPIResource):
    """One stablecoin balance (``currency``: USDT by default, or USDC). Never converted to VES."""

    async def retrieve(self, params: Optional[Params] = None, **options: Unpack[RequestOptions]) -> m.CryptoBalanceDto:
        return await self._request_model("Crypto_getBalance", m.CryptoBalanceDto, query=params or {}, options=options)


class AsyncCryptoBalances(AsyncAPIResource):
    """Every stablecoin balance (USDT and USDC)."""

    async def list(self, **options: Unpack[RequestOptions]) -> m.CryptoBalancesDto:
        return await self._request_model("Crypto_getBalances", m.CryptoBalancesDto, options=options)


class AsyncDepositAddresses(AsyncAPIResource):
    """Static deposit addresses per customer, stablecoin (``currency``) and network."""

    async def create(
        self, params: Union[m.CreateDepositAddressDto, Params], **options: Unpack[RequestOptions]
    ) -> m.DepositAddressDto:
        """Get or create — the same customer and network always return the same address."""
        return await self._request_model("Crypto_createDepositAddress", m.DepositAddressDto, body=params, options=options)


class AsyncCryptoNetworks(AsyncAPIResource):
    """Enabled networks for one stablecoin (``currency``) with the payout fee and availability for an amount."""

    async def list(self, params: Optional[Params] = None, **options: Unpack[RequestOptions]) -> list[m.CryptoNetworkDto]:
        raw = await self._request_json("Crypto_listNetworks", query=params or {}, options=options)
        return [m.CryptoNetworkDto.model_validate(n) for n in raw]


class AsyncCryptoPayouts(AsyncAPIResource):
    """Stablecoin payouts (``currency``: USDT or USDC). ``idempotencyKey`` (in the body) makes retries safe."""

    async def create(
        self, params: Union[m.CreateCryptoPayoutDto, Params], **options: Unpack[RequestOptions]
    ) -> m.CryptoPayoutDto:
        return await self._request_model("Crypto_createPayout", m.CryptoPayoutDto, body=params, options=options)

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.CryptoPayoutDto:
        return await self._request_model("Crypto_getPayout", m.CryptoPayoutDto, path={"id": id}, options=options)


class AsyncCrypto(AsyncAPIResource):
    """Stablecoins (USDT, USDC): deposit addresses, balances, networks and payouts."""

    def __init__(self, http: Any) -> None:
        super().__init__(http)
        self.balance = AsyncCryptoBalance(self._http)
        self.balances = AsyncCryptoBalances(self._http)
        self.deposit_addresses = AsyncDepositAddresses(self._http)
        self.networks = AsyncCryptoNetworks(self._http)
        self.payouts = AsyncCryptoPayouts(self._http)

class AsyncCopPayments(AsyncAPIResource):
    """Colombian peso payments: PSE and Bancolombia (bank redirect), Bancolombia QR, Bre-B (QR / transfer
    key), Nequi (push approval) or Daviplata (SMS code or redirect). Cards are taken only on the hosted checkout.

    Payments complete asynchronously — listen for ``payment.completed`` / ``payment.failed``.
    COP must be enabled on your account (403 ``method_not_allowed`` otherwise).
    """

    async def create(
        self, params: Union[m.CreateCopPaymentDto, Params], **options: Unpack[RequestOptions]
    ) -> m.CopPaymentDto:
        """Create a payment in whole pesos; ``buyer`` is required for every channel except ``breb``.

        Send ``buyer.termsAccepted: true`` when ``cop.channels()`` says ``needsTermsAcceptance``; ``pse`` also
        needs ``pse.bankCode``. ``next.type`` says what the buyer does: ``show_qr``, ``approve_in_app``,
        ``submit_otp``, ``redirect`` (send them to ``next.url``) or ``redirect_pending`` (retrieve again shortly).
        Pass ``idempotency_key`` to retry safely.
        """
        return await self._request_model("CopPayments_create", m.CopPaymentDto, body=params, options=options)

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.CopPaymentDto:
        return await self._request_model("CopPayments_get", m.CopPaymentDto, path={"id": id}, options=options)

    async def submit_otp(
        self, id: str, params: Union[m.SubmitCopOtpDto, Params], **options: Unpack[RequestOptions]
    ) -> m.CopPaymentDto:
        """Daviplata with ``next.type == "submit_otp"``: submit the SMS code. A wrong code fails with ``invalid_otp``."""
        return await self._request_model("CopPayments_submitOtp", m.CopPaymentDto, path={"id": id}, body=params, options=options)

    async def cancel(self, id: str, **options: Unpack[RequestOptions]) -> m.CopPaymentDto:
        """Cancel a pending payment."""
        return await self._request_model("CopPayments_cancel", m.CopPaymentDto, path={"id": id}, options=options)

    async def refund(self, id: str, **options: Unpack[RequestOptions]) -> m.CopPaymentDto:
        """Full refund of a completed payment (card within 24 h, Bre-B within 96 h).

        Channels that cannot be refunded through the API fail with ``refund_not_supported``.
        """
        return await self._request_model("CopPayments_refund", m.CopPaymentDto, path={"id": id}, options=options)


class AsyncCopBalance(AsyncAPIResource):
    """Your COP balance, in whole pesos. Kept apart from VES and stablecoins."""

    async def retrieve(self, **options: Unpack[RequestOptions]) -> m.CopBalanceDto:
        return await self._request_model("CopPayments_balance", m.CopBalanceDto, options=options)


class AsyncCop(AsyncAPIResource):
    """Collect Colombian pesos (PSE, Bancolombia, Bre-B, Nequi, Daviplata; cards via the hosted checkout)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http)
        self.payments = AsyncCopPayments(self._http)
        self.balance = AsyncCopBalance(self._http)

    async def channels(self, **options: Unpack[RequestOptions]) -> m.CopChannelsDto:
        """Channels you can use right now, with what each needs, plus the PSE banks and terms links."""
        return await self._request_model("CopPayments_channels", m.CopChannelsDto, options=options)


class AsyncConversionQuotes(AsyncAPIResource):
    """A rate for converting VES or COP to USDT, locked for 60 seconds."""

    async def create(
        self, params: Union[m.CreateConversionQuoteDto, Params], **options: Unpack[RequestOptions]
    ) -> m.ConversionQuoteDto:
        """``sourceCurrency`` is ``"VES"`` (default) or ``"COP"``. Send ``sourceAmount`` (to spend; COP in whole
        pesos) or ``targetAmountUsdt`` (USDT to receive) — exactly one. VES may still use ``sourceAmountVes``."""
        return await self._request_model("Conversions_createQuote", m.ConversionQuoteDto, body=params, options=options)


class AsyncConversionSettings(AsyncAPIResource):
    """Your conversion spreads, minimum and caps, and COP auto-convert."""

    async def retrieve(self, **options: Unpack[RequestOptions]) -> m.ConversionSettingsDto:
        return await self._request_model("ConversionSettings_get", m.ConversionSettingsDto, options=options)

    async def update(
        self, params: Union[m.UpdateConversionSettingsDto, Params], **options: Unpack[RequestOptions]
    ) -> m.ConversionSettingsDto:
        """Only ``autoConvert.COP.percent`` (0–100, whole number; 0 = off) can be changed."""
        return await self._request_model("ConversionSettings_update", m.ConversionSettingsDto, body=params, options=options)


class AsyncConversions(AsyncAPIResource):
    """Convert available VES or COP into your USDT balance (enabled per account).

    Accepting a quote debits the source at once (``conversion.created``); the conversion is ``PENDING``
    until VEXPay delivers the USDT (``conversion.completed``).
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http)
        self.quotes = AsyncConversionQuotes(self._http)
        self.settings = AsyncConversionSettings(self._http)

    async def create(
        self, params: Union[m.CreateConversionDto, Params], **options: Unpack[RequestOptions]
    ) -> m.ConversionDto:
        """Accept a quote (``quoteId``). Pass ``idempotency_key`` to retry safely."""
        return await self._request_model("Conversions_create", m.ConversionDto, body=params, options=options)

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.ConversionDto:
        return await self._request_model("Conversions_get", m.ConversionDto, path={"id": id}, options=options)

    def list(
        self, params: Optional[Params] = None, **options: Unpack[RequestOptions]
    ) -> AsyncPage[m.ConversionListDto, m.ConversionDto]:
        query = dict(params or {})
        return AsyncPage(
            lambda cursor: self._request_model(
                "Conversions_list", m.ConversionListDto, query={**query, "cursor": cursor}, options=options
            ),
            query.get("cursor"),
        )

    async def cancel(self, id: str, **options: Unpack[RequestOptions]) -> m.ConversionDto:
        """Cancel a ``PENDING`` conversion; the VES or COP returns to your available balance."""
        return await self._request_model("Conversions_cancel", m.ConversionDto, path={"id": id}, options=options)


# ── billing ───────────────────────────────────────────────────────────────────


class AsyncCustomerPaymentMethods(AsyncAPIResource):
    """A customer's attached domiciliación payment methods."""

    def list(
        self, customer_id: str, params: Optional[Params] = None, **options: Unpack[RequestOptions]
    ) -> AsyncPage[m.PaymentMethodListResponseDto, m.PaymentMethodResponseDto]:
        """Newest first."""
        query = dict(params or {})
        return AsyncPage(
            lambda cursor: self._request_model(
                "PaymentMethods_list",
                m.PaymentMethodListResponseDto,
                path={"id": customer_id},
                query={**query, "cursor": cursor},
                options=options,
            ),
            query.get("cursor"),
        )


class AsyncCustomers(AsyncAPIResource):
    """Billing customers: who subscriptions and invoices belong to."""

    def __init__(self, http: Any) -> None:
        super().__init__(http)
        self.payment_methods = AsyncCustomerPaymentMethods(self._http)

    async def create(
        self, params: Union[m.CreateCustomerDto, Params], **options: Unpack[RequestOptions]
    ) -> m.CustomerResponseDto:
        return await self._request_model("Customers_create", m.CustomerResponseDto, body=params, options=options)

    def list(
        self, params: Optional[Params] = None, **options: Unpack[RequestOptions]
    ) -> AsyncPage[m.CustomerListResponseDto, m.CustomerResponseDto]:
        """Newest first; filter by ``email``."""
        query = dict(params or {})
        return AsyncPage(
            lambda cursor: self._request_model(
                "Customers_list", m.CustomerListResponseDto, query={**query, "cursor": cursor}, options=options
            ),
            query.get("cursor"),
        )

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.CustomerResponseDto:
        return await self._request_model("Customers_retrieve", m.CustomerResponseDto, path={"id": id}, options=options)

    async def update(
        self, id: str, params: Union[m.UpdateCustomerDto, Params], **options: Unpack[RequestOptions]
    ) -> m.CustomerResponseDto:
        """``None`` clears a field."""
        return await self._request_model(
            "Customers_update", m.CustomerResponseDto, path={"id": id}, body=params, options=options
        )

    async def delete(self, id: str, **options: Unpack[RequestOptions]) -> m.DeletedObjectResponseDto:
        """Only a customer with no live subscriptions can be deleted."""
        return await self._request_model("Customers_remove", m.DeletedObjectResponseDto, path={"id": id}, options=options)


class AsyncPrices(AsyncAPIResource):
    """Recurring USD prices on a product."""

    async def create(
        self, params: Union[m.CreatePriceDto, Params], **options: Unpack[RequestOptions]
    ) -> m.PriceResponseDto:
        return await self._request_model("Prices_create", m.PriceResponseDto, body=params, options=options)

    def list(
        self, params: Optional[Params] = None, **options: Unpack[RequestOptions]
    ) -> AsyncPage[m.PriceListResponseDto, m.PriceResponseDto]:
        """Filter by ``product`` and ``active``."""
        query = dict(params or {})
        return AsyncPage(
            lambda cursor: self._request_model(
                "Prices_list", m.PriceListResponseDto, query={**query, "cursor": cursor}, options=options
            ),
            query.get("cursor"),
        )

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.PriceResponseDto:
        return await self._request_model("Prices_retrieve", m.PriceResponseDto, path={"id": id}, options=options)

    async def update(
        self, id: str, params: Union[m.UpdatePriceDto, Params], **options: Unpack[RequestOptions]
    ) -> m.PriceResponseDto:
        """Only ``active``, ``nickname`` and ``metadata`` can change; the amount and interval are fixed."""
        return await self._request_model("Prices_update", m.PriceResponseDto, path={"id": id}, body=params, options=options)


class AsyncSubscriptions(AsyncAPIResource):
    """Bill a customer on a recurring price (``send_invoice`` or ``charge_automatically``)."""

    async def create(
        self, params: Union[m.CreateSubscriptionDto, Params], **options: Unpack[RequestOptions]
    ) -> m.SubscriptionResponseDto:
        """Pass ``idempotency_key`` to retry safely."""
        return await self._request_model("Subscriptions_create", m.SubscriptionResponseDto, body=params, options=options)

    def list(
        self, params: Optional[Params] = None, **options: Unpack[RequestOptions]
    ) -> AsyncPage[m.SubscriptionListResponseDto, m.SubscriptionResponseDto]:
        """Newest first; filter by ``customer``, ``price`` and ``status``."""
        query = dict(params or {})
        return AsyncPage(
            lambda cursor: self._request_model(
                "Subscriptions_list", m.SubscriptionListResponseDto, query={**query, "cursor": cursor}, options=options
            ),
            query.get("cursor"),
        )

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.SubscriptionResponseDto:
        return await self._request_model(
            "Subscriptions_retrieve", m.SubscriptionResponseDto, path={"id": id}, options=options
        )

    async def update(
        self, id: str, params: Union[m.UpdateSubscriptionDto, Params], **options: Unpack[RequestOptions]
    ) -> m.SubscriptionResponseDto:
        """Changes apply from the next invoice."""
        return await self._request_model(
            "Subscriptions_update", m.SubscriptionResponseDto, path={"id": id}, body=params, options=options
        )

    async def cancel(self, id: str, **options: Unpack[RequestOptions]) -> m.SubscriptionResponseDto:
        """Cancel now and void its open invoices. To stop at the period end, ``update`` ``cancelAtPeriodEnd``."""
        return await self._request_model("Subscriptions_cancel", m.SubscriptionResponseDto, path={"id": id}, options=options)


class AsyncInvoices(AsyncAPIResource):
    """Invoices that subscriptions issue each period."""

    def list(
        self, params: Optional[Params] = None, **options: Unpack[RequestOptions]
    ) -> AsyncPage[m.InvoiceListResponseDto, m.InvoiceResponseDto]:
        """Newest first; filter by ``customer``, ``subscription`` and ``status``."""
        query = dict(params or {})
        return AsyncPage(
            lambda cursor: self._request_model(
                "Invoices_list", m.InvoiceListResponseDto, query={**query, "cursor": cursor}, options=options
            ),
            query.get("cursor"),
        )

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.InvoiceResponseDto:
        return await self._request_model("Invoices_retrieve", m.InvoiceResponseDto, path={"id": id}, options=options)

    async def void(self, id: str, **options: Unpack[RequestOptions]) -> m.InvoiceResponseDto:
        """Void an open invoice."""
        return await self._request_model("Invoices_void", m.InvoiceResponseDto, path={"id": id}, options=options)

    async def mark_uncollectible(self, id: str, **options: Unpack[RequestOptions]) -> m.InvoiceResponseDto:
        """Mark an open invoice uncollectible; it stays payable."""
        return await self._request_model(
            "Invoices_markUncollectible", m.InvoiceResponseDto, path={"id": id}, options=options
        )

    async def pay(
        self, id: str, params: Union[m.PayInvoiceDto, Params], **options: Unpack[RequestOptions]
    ) -> m.InvoiceResponseDto:
        """Mark an open invoice paid outside VEXPay (``{"paidOutOfBand": True}``). No payment, no balance change."""
        return await self._request_model("Invoices_pay", m.InvoiceResponseDto, path={"id": id}, body=params, options=options)


class AsyncSetupSessions(AsyncAPIResource):
    """Hosted links where a customer authorizes a domiciliación (expire in 24 h)."""

    async def create(
        self, params: Union[m.CreateSetupSessionDto, Params], **options: Unpack[RequestOptions]
    ) -> m.SetupSessionResponseDto:
        """``url`` is returned only here — send the customer to it."""
        return await self._request_model("SetupSessions_create", m.SetupSessionResponseDto, body=params, options=options)

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.SetupSessionResponseDto:
        return await self._request_model(
            "SetupSessions_retrieve", m.SetupSessionResponseDto, path={"id": id}, options=options
        )


class AsyncPaymentMethods(AsyncAPIResource):
    """Domiciliación payment methods. List a customer's with ``customers.payment_methods.list``."""

    async def retrieve(self, id: str, **options: Unpack[RequestOptions]) -> m.PaymentMethodResponseDto:
        return await self._request_model(
            "PaymentMethods_retrieve", m.PaymentMethodResponseDto, path={"id": id}, options=options
        )

    async def detach(self, id: str, **options: Unpack[RequestOptions]) -> m.PaymentMethodResponseDto:
        """A detached method is never charged again."""
        return await self._request_model(
            "PaymentMethods_detach", m.PaymentMethodResponseDto, path={"id": id}, options=options
        )
