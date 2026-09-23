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
    """Débito inmediato (requires R4)."""

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
    """Crédito inmediato and disbursements (requires R4)."""

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
    """Bank operation status for débito/crédito (requires R4)."""

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
    """Account payout dispersion (requires R4)."""

    async def create(
        self, params: Union[m.PayoutDto, Params], **options: Unpack[RequestOptions]
    ) -> m.AccountPayoutDispersionResponseDto:
        return await self._request_model(
            "R4Operations_dispersarPagos", m.AccountPayoutDispersionResponseDto, body=params, options=options
        )


class AsyncChange(AsyncAPIResource):
    """Vuelto / change payments (requires R4)."""

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
    ) -> m.MerchantBalanceDto:
        """Move VES between this merchant's balance and another."""
        return await self._request_model(
            "Merchants_transfer", m.MerchantBalanceDto, path={"id": id}, body=params, options=options
        )

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


class AsyncBalance(AsyncAPIResource):
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
