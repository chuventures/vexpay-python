# Generated from packages/sdk-spec/openapi.json by scripts/generate-models.sh — do not edit.


from __future__ import annotations

from datetime import date
from typing import Any, Literal, Optional, Union

from pydantic import AnyUrl, AwareDatetime, BaseModel, Field


class ApiErrorDto(BaseModel):
    statusCode: Optional[float] = Field(None, examples=[400])
    """
    HTTP status code mirrored in the JSON body (Nest default error shape). Absent on domain errors.
    """
    message: Optional[Union[str, list[str]]] = Field(
        None, examples=["usdAmount must be a positive number"]
    )
    """
    Human-readable error detail, or a validation error array.
    """
    error: Optional[str] = Field(None, examples=["insufficient_balance"])
    """
    Machine-readable error code (e.g. `external_ref_conflict`, `insufficient_balance`, `idempotency_key_reused`, `live_mode_not_activated`) or, for Nest default errors, a short label such as `Bad Request`. Domain errors may include extra route-specific fields.
    """


class PlatformBalanceDto(BaseModel):
    tenantId: str
    platformId: str = Field(..., examples=["plt_3fd84b2d9ad14f74a2d90f2f56984db5"])
    collectedVes: str = Field(..., examples=["10000.00"])
    feesVes: str = Field(..., examples=["250.00"])
    paidOutVes: str = Field(..., examples=["1000.00"])
    convertedVes: str = Field(..., examples=["0.00"])
    """
    Net VES spent on VES→USDT conversions.
    """
    chargebackFeesVes: str = Field(..., examples=["0.00"])
    """
    Net card chargeback fees charged (fees minus fees returned on won disputes).
    """
    reserveVes: str = Field(..., examples=["100.00"])
    ledgerNetVes: str = Field(..., examples=["8650.00"])
    heldVes: Optional[str] = Field(None, examples=["4500.00"])
    """
    VES under the 24h balance hold: incoming credits count in `ledgerNetVes` but cannot be paid out until their hold ends. Conversions and seller transfers may still use them.
    """
    nextReleaseAt: Optional[AwareDatetime] = Field(
        None, examples=["2026-10-20T00:48:52.784Z"]
    )
    """
    When the soonest held amount becomes available; null when nothing is held.
    """
    availableVes: str = Field(..., examples=["4150.00"])
    """
    What payouts can spend: ledgerNetVes − reserveVes − heldVes (seller obligations already deducted via SELLER_TRANSFER).
    """
    platformAvailableVes: str = Field(..., examples=["8650.00"])
    sellerObligationsVes: str = Field(..., examples=["1200.00"])
    """
    Sum of seller pending + available obligations.
    """
    sellerPendingVes: str = Field(..., examples=["400.00"])
    sellerAvailableVes: str = Field(..., examples=["800.00"])
    feePercent: str = Field(..., examples=["2.5000"])
    feeFixedUsd: str = Field(..., examples=["0.00"])
    balanceHoldHours: Optional[float] = Field(None, examples=[24])
    """
    Hours each incoming credit is held before payouts can spend it (0 = no hold). Set by VEXPay.
    """


class BalanceTransactionDto(BaseModel):
    id: str
    """
    Stable id of the movement; never changes or disappears.
    """
    type: Literal[
        "payment",
        "fee",
        "payment_reversal",
        "fee_reversal",
        "payout",
        "payout_reversal",
        "chargeback",
        "chargeback_fee",
        "chargeback_reversal",
        "adjustment",
        "seller_transfer",
        "seller_transfer_reversal",
        "conversion",
        "conversion_reversal",
        "merchant_payout_fee",
        "disbursement_payout_fee",
        "disbursement_payout_fee_reversal",
        "topup",
        "topup_fee",
        "topup_instant_release",
        "topup_instant_fee",
    ] = Field(..., examples=["chargeback"])
    amountVes: str = Field(..., examples=["-4000.00"])
    """
    Signed VES amount (negative = money out of your balance).
    """
    paymentId: Optional[str] = None
    payoutId: Optional[str] = None
    chargebackId: Optional[str] = None
    """
    Present on chargeback movements.
    """
    merchantId: Optional[str] = None
    externalRef: Optional[str] = Field(None, examples=["order-1042"])
    """
    externalRef of the linked payment or payout.
    """
    description: str = Field(..., examples=["Card chargeback (fraud)"])
    availableAt: Optional[AwareDatetime] = None
    """
    Part of the 24h balance hold: this movement counts in `heldVes` (not `availableVes`) until this time.
    """
    createdAt: AwareDatetime


class BalanceTransactionListDto(BaseModel):
    items: list[BalanceTransactionDto]
    nextCursor: Optional[str] = Field(...)
    """
    Pass as `cursor` to get the next (older) page; null on the last page.
    """


class CreateWebhookDto(BaseModel):
    url: AnyUrl = Field(..., examples=["https://merchant.example.com/webhooks/vexpay"])
    secret: Optional[str] = Field(None, examples=["replace-with-a-long-random-secret"])
    """
    Signing secret. If omitted, a random secret is generated and returned once.
    """
    events: list[
        Literal[
            "payment.pending",
            "payment.completed",
            "payment.failed",
            "payment.canceled",
            "payment.reversed",
            "payment.chargeback",
            "payment.chargeback_closed",
            "merchant.verified",
            "merchant.rejected",
            "merchant.deactivated",
            "merchant.reactivated",
            "merchant.balance.updated",
            "merchant.created",
            "merchant.activated",
            "merchant.updated",
            "merchant.kyb_required",
            "merchant.restricted",
            "merchant.capability.updated",
            "merchant.wallet_credit",
            "payout.completed",
            "payout.failed",
            "conversion.created",
            "conversion.completed",
            "conversion.canceled",
            "onward_payout.updated",
            "tenant.status_changed",
            "tenant.api_key.created",
            "tenant.api_key.rotated",
            "tenant.api_key.revoked",
            "tenant.live_status_changed",
            "customer.created",
            "customer.updated",
            "customer.deleted",
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
            "customer.subscription.trial_will_end",
            "customer.subscription.reactivated",
            "invoice.created",
            "invoice.upcoming",
            "invoice.paid",
            "invoice.payment_attempt",
            "invoice.payment_failed",
            "invoice.overdue",
            "invoice.voided",
            "invoice.marked_uncollectible",
            "payment_method.attached",
            "payment_method.updated",
            "payment_method.detached",
            "notification.test",
        ]
    ] = Field(..., examples=[["payment.completed", "payment.failed"]])


class WebhookEndpointDto(BaseModel):
    id: str
    tenantId: str
    url: AnyUrl
    events: list[
        Literal[
            "payment.pending",
            "payment.completed",
            "payment.failed",
            "payment.canceled",
            "payment.reversed",
            "payment.chargeback",
            "payment.chargeback_closed",
            "merchant.verified",
            "merchant.rejected",
            "merchant.deactivated",
            "merchant.reactivated",
            "merchant.balance.updated",
            "merchant.created",
            "merchant.activated",
            "merchant.updated",
            "merchant.kyb_required",
            "merchant.restricted",
            "merchant.capability.updated",
            "merchant.wallet_credit",
            "payout.completed",
            "payout.failed",
            "conversion.created",
            "conversion.completed",
            "conversion.canceled",
            "onward_payout.updated",
            "tenant.status_changed",
            "tenant.api_key.created",
            "tenant.api_key.rotated",
            "tenant.api_key.revoked",
            "tenant.live_status_changed",
            "customer.created",
            "customer.updated",
            "customer.deleted",
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
            "customer.subscription.trial_will_end",
            "customer.subscription.reactivated",
            "invoice.created",
            "invoice.upcoming",
            "invoice.paid",
            "invoice.payment_attempt",
            "invoice.payment_failed",
            "invoice.overdue",
            "invoice.voided",
            "invoice.marked_uncollectible",
            "payment_method.attached",
            "payment_method.updated",
            "payment_method.detached",
            "notification.test",
        ]
    ]
    isActive: bool
    createdAt: AwareDatetime
    secret: Optional[str] = None
    """
    Returned only when the endpoint is created. Store it securely; list responses omit it.
    """


class UpdateWebhookDto(BaseModel):
    url: Optional[AnyUrl] = Field(
        None, examples=["https://merchant.example.com/webhooks/vexpay"]
    )
    events: Optional[
        list[
            Literal[
                "payment.pending",
                "payment.completed",
                "payment.failed",
                "payment.canceled",
                "payment.reversed",
                "payment.chargeback",
                "payment.chargeback_closed",
                "merchant.verified",
                "merchant.rejected",
                "merchant.deactivated",
                "merchant.reactivated",
                "merchant.balance.updated",
                "merchant.created",
                "merchant.activated",
                "merchant.updated",
                "merchant.kyb_required",
                "merchant.restricted",
                "merchant.capability.updated",
                "merchant.wallet_credit",
                "payout.completed",
                "payout.failed",
                "conversion.created",
                "conversion.completed",
                "conversion.canceled",
                "onward_payout.updated",
                "tenant.status_changed",
                "tenant.api_key.created",
                "tenant.api_key.rotated",
                "tenant.api_key.revoked",
                "tenant.live_status_changed",
                "customer.created",
                "customer.updated",
                "customer.deleted",
                "customer.subscription.created",
                "customer.subscription.updated",
                "customer.subscription.deleted",
                "customer.subscription.trial_will_end",
                "customer.subscription.reactivated",
                "invoice.created",
                "invoice.upcoming",
                "invoice.paid",
                "invoice.payment_attempt",
                "invoice.payment_failed",
                "invoice.overdue",
                "invoice.voided",
                "invoice.marked_uncollectible",
                "payment_method.attached",
                "payment_method.updated",
                "payment_method.detached",
                "notification.test",
            ]
        ]
    ] = Field(
        None, examples=[["payment.completed", "payment.failed", "payout.completed"]]
    )
    """
    Replaces the full event subscription list when provided.
    """
    isActive: Optional[bool] = Field(None, examples=[True])


class DeleteWebhookResponseDto(BaseModel):
    deleted: bool = Field(..., examples=[True])


class PayoutResponseDto(BaseModel):
    payoutId: str
    """
    Payout id. Empty string only on batch item failures that never created a row.
    """
    status: Literal["completed", "pending", "failed", "awaiting_approval"]
    """
    `pending` means the credit is still reconciling (AC00); subscribe to payout webhooks or poll GET /v1/payouts/:id. `awaiting_approval` means the funds are reserved but the payout is held for VEX Pay review (see `holdReason`) and has not been sent; it later becomes `pending`/`completed` when approved or `failed` (`rejected_new_account_limit`, funds returned) when rejected.
    """
    holdReason: Optional[Literal["NEW_ACCOUNT_LIMIT"]] = None
    """
    Why the payout was held for review. `NEW_ACCOUNT_LIMIT`: the tenant or merchant is new (first 30 days) and this payout would take its rolling 24h money-out above the new-account cap (default US$300 equivalent).
    """
    reference: Optional[str] = None
    """
    Bank reference when available.
    """
    failureCode: Optional[str] = None
    """
    Machine-readable failure when status is failed (e.g. merchant_inactive, payout_method_not_verified).
    """
    externalRef: Optional[str] = None
    """
    Tenant-supplied idempotency / lookup key.
    """
    paymentId: Optional[str] = None
    """
    Funding payment when this payout is a marketplace settlement leg.
    """
    merchantId: Optional[str] = None
    payoutMethodId: Optional[str] = None
    merchantName: Optional[str] = None
    monto: Optional[str] = Field(None, examples=["1523.40"])
    """
    Net two-decimal VES amount credited at the bank.
    """
    grossMonto: Optional[str] = Field(None, examples=["100.00"])
    """
    Gross VES withdrawn from the ledger (instant tenant credits only).
    """
    feePercent: Optional[str] = Field(None, examples=["2.5000"])
    """
    Platform fee percent applied on instant tenant credits.
    """
    feeVes: Optional[str] = Field(None, examples=["2.50"])
    """
    Platform fee in VES: retained on instant tenant credits, or the end-user withdrawal fee on a disbursement payout (see feePayer).
    """
    feePayer: Optional[Literal["tenant"]] = Field(None, examples=["tenant"])
    """
    Set to "tenant" when your balance paid feeVes (disbursement withdrawal fee): the end user was debited only monto.
    """
    concepto: Optional[str] = None
    bankCode: Optional[str] = Field(None, examples=["0134"])
    """
    Destination bank SIMF code.
    """
    destination: Optional[str] = None
    """
    Masked phone destination, e.g. …5555
    """
    operationId: Optional[str] = None
    """
    Network operation id while pending reconciliation.
    """
    createdAt: Optional[AwareDatetime] = None
    settledAt: Optional[AwareDatetime] = None


class PayoutListResponseDto(BaseModel):
    items: list[PayoutResponseDto]
    nextCursor: Optional[str] = None
    """
    Pass as cursor on the next request when more pages exist
    """


class PayoutBatchItemResultDto(BaseModel):
    payoutId: str
    """
    Payout id. Empty string only on batch item failures that never created a row.
    """
    status: Literal["completed", "pending", "failed", "awaiting_approval"]
    """
    `pending` means the credit is still reconciling (AC00); subscribe to payout webhooks or poll GET /v1/payouts/:id. `awaiting_approval` means the funds are reserved but the payout is held for VEX Pay review (see `holdReason`) and has not been sent; it later becomes `pending`/`completed` when approved or `failed` (`rejected_new_account_limit`, funds returned) when rejected.
    """
    holdReason: Optional[Literal["NEW_ACCOUNT_LIMIT"]] = None
    """
    Why the payout was held for review. `NEW_ACCOUNT_LIMIT`: the tenant or merchant is new (first 30 days) and this payout would take its rolling 24h money-out above the new-account cap (default US$300 equivalent).
    """
    reference: Optional[str] = None
    """
    Bank reference when available.
    """
    failureCode: Optional[str] = None
    """
    Machine-readable failure when status is failed (e.g. merchant_inactive, payout_method_not_verified).
    """
    externalRef: Optional[str] = Field(None, max_length=64)
    """
    Echo of the item-level externalRef from the request (idempotency key).
    """
    paymentId: Optional[str] = None
    """
    Funding payment when this payout is a marketplace settlement leg.
    """
    merchantId: Optional[str] = None
    payoutMethodId: Optional[str] = None
    merchantName: Optional[str] = None
    monto: Optional[str] = Field(None, examples=["1523.40"])
    """
    Net two-decimal VES amount credited at the bank.
    """
    grossMonto: Optional[str] = Field(None, examples=["100.00"])
    """
    Gross VES withdrawn from the ledger (instant tenant credits only).
    """
    feePercent: Optional[str] = Field(None, examples=["2.5000"])
    """
    Platform fee percent applied on instant tenant credits.
    """
    feeVes: Optional[str] = Field(None, examples=["2.50"])
    """
    Platform fee in VES: retained on instant tenant credits, or the end-user withdrawal fee on a disbursement payout (see feePayer).
    """
    feePayer: Optional[Literal["tenant"]] = Field(None, examples=["tenant"])
    """
    Set to "tenant" when your balance paid feeVes (disbursement withdrawal fee): the end user was debited only monto.
    """
    concepto: Optional[str] = None
    bankCode: Optional[str] = Field(None, examples=["0134"])
    """
    Destination bank SIMF code.
    """
    destination: Optional[str] = None
    """
    Masked phone destination, e.g. …5555
    """
    operationId: Optional[str] = None
    """
    Network operation id while pending reconciliation.
    """
    createdAt: Optional[AwareDatetime] = None
    settledAt: Optional[AwareDatetime] = None


class PayoutBatchResponseDto(BaseModel):
    batchId: str
    """
    Batch id. Same payload + batch externalRef replays with 200.
    """
    paymentId: Optional[str] = None
    """
    Funding payment when this batch settles a marketplace collection.
    """
    items: list[PayoutBatchItemResultDto]
    """
    Per-item results in request order. Failed items include status `failed` and failureCode; they do not abort the rest of the batch.
    """


class CreatePayoutDto(BaseModel):
    merchantId: str
    """
    Verified, active merchant that receives the payout.
    """
    payoutMethodId: Optional[str] = None
    """
    Payout method to credit. Defaults to the merchant’s default verified method when omitted.
    """
    monto: str = Field(..., examples=["1523.40"])
    """
    Exact two-decimal VES amount as a string. The gateway never converts FX for payouts.
    """
    concepto: str = Field(..., examples=["Liquidacion semana 30"], max_length=30)
    """
    Statement concept (max 30 chars).
    """
    externalRef: str = Field(..., examples=["po_9c21…"], max_length=64)
    """
    Required idempotency key per tenant. Same payload → 200 replay; conflicting payload → 409 external_ref_conflict.
    """
    paymentId: Optional[str] = None
    """
    Optional funding payment for marketplace settlement. When set, montos are capped by remaining net (vesAmount − feeVes − PENDING/COMPLETED payouts). Multiple payouts allowed until remaining is 0.
    """
    fromMerchantBalance: Optional[bool] = None
    """
    When true, debit the seller available balance (tenant float already reserved via SELLER_TRANSFER). Default false = classic tenant-float payout.
    """


class CreateInstantPayoutDto(BaseModel):
    monto: str = Field(..., examples=["100.00"])
    """
    Gross two-decimal VES amount to withdraw from the tenant ledger. Credits the tenant’s verified payout account (net of feePercent). Requires a verified eligible account (cooling only after destination change).
    """
    concepto: str = Field(..., examples=["Retiro tenant"], max_length=30)
    """
    Statement concept (max 30 chars).
    """
    externalRef: str = Field(..., examples=["ti_9c21…"], max_length=64)
    """
    Required idempotency key per tenant. Same payload → 200 replay; conflicting payload → 409 external_ref_conflict.
    """


class BatchPayoutItemDto(BaseModel):
    merchantId: str
    payoutMethodId: Optional[str] = None
    """
    Payout method to credit. Defaults to the merchant’s default verified method when omitted.
    """
    monto: str = Field(..., examples=["1523.40"])
    concepto: str = Field(..., max_length=30)
    externalRef: str = Field(..., max_length=64)
    fromMerchantBalance: Optional[bool] = None
    """
    When true, debit the seller available balance instead of tenant float.
    """


class CreatePayoutBatchDto(BaseModel):
    externalRef: str = Field(..., examples=["corte_2026-07-28"], max_length=64)
    """
    Batch-level idempotency key. Same externalRef + identical items → 200 replay; conflict → 409.
    """
    paymentId: Optional[str] = None
    """
    Optional funding payment for marketplace settlement. Applied to every item. Sum of item montos must fit remaining net for that payment.
    """
    items: list[BatchPayoutItemDto]
    """
    One or more payout legs. Each item has its own externalRef (also idempotent). Failed items do not roll back successful siblings.
    """


class TenantPayoutAccountResponseDto(BaseModel):
    accountId: str
    bankCode: str = Field(..., examples=["0163"])
    destination: str
    """
    Masked phone, e.g. …5555
    """
    identification: str = Field(..., examples=["V12345678"])
    eligibility: Literal[
        "pending_verification", "verifying", "cooling", "eligible", "rejected", "locked"
    ]
    """
    UI/API eligibility state. `cooling` = verified after a destination change, still within the 1 business-day wait. `eligible` = may receive instant credits (first verify unlocks immediately).
    """
    status: Literal["pending_verification", "verifying", "verified", "rejected"]
    verifiedAt: Optional[AwareDatetime] = None
    payoutEligibleAt: Optional[AwareDatetime] = None
    """
    Instant payouts allowed at/after this timestamp (verifiedAt + 1 business day).
    """
    failureCode: Optional[str] = None
    lockedUntil: Optional[AwareDatetime] = None
    verifyExpiresAt: Optional[AwareDatetime] = None
    """
    When the current micro-deposit confirm window expires.
    """


class TenantPayoutAccountVerifyStartResponseDto(BaseModel):
    status: Literal["verifying"]
    expiresAt: AwareDatetime
    accountId: str


class TenantPayoutAccountVerifyConfirmResponseDto(BaseModel):
    status: Literal["eligible", "cooling"]
    """
    `eligible` on first successful verify (instant credits allowed immediately). `cooling` after a destination change re-verify (1 business day).
    """
    accountId: str
    payoutEligibleAt: AwareDatetime


class UpsertTenantPayoutAccountDto(BaseModel):
    banco: str = Field(..., examples=["0163"])
    """
    Beneficiary bank SIMF code (3–4 digits). Prefer codes from GET /v1/banks.
    """
    cedula: str = Field(..., examples=["V12345678"])
    """
    Beneficiary cédula/RIF.
    """
    telefono: str = Field(..., examples=["584121234567"])
    """
    Beneficiary Pago Móvil phone (58… or 0…).
    """


class ConfirmTenantPayoutAccountVerifyDto(BaseModel):
    amount1: str = Field(..., examples=["0.37"])
    """
    First micro-deposit amount (exact two decimals).
    """
    amount2: str = Field(..., examples=["0.12"])
    """
    Second micro-deposit amount (exact two decimals).
    """


class DebitOtpResponseDto(BaseModel):
    code: str = Field(..., examples=["202"])
    """
    Typically `202` when the payer bank accepted the OTP request and will SMS the customer.
    """
    message: Optional[str] = Field(None, examples=["Operación aceptada"])
    """
    Human-readable network message when provided.
    """
    reference: Optional[str] = Field(None, examples=["16142940"])
    """
    Bank reference when the operation settles synchronously.
    """
    id: Optional[str] = Field(None, examples=["6785d97e-2092-49f0-9f7d-3d5921f0b13f"])
    """
    Network operation id. Prefer this over `Id` when both are present. Use with GET /v1/payments/operations/:id.
    """
    Id: Optional[str] = Field(None, examples=["6785d97e-2092-49f0-9f7d-3d5921f0b13f"])
    """
    Alternate casing of the operation id some network responses use.
    """
    success: Optional[bool] = Field(None, examples=[True])
    """
    Present on some operation responses when the network returns an explicit success flag.
    """


class ImmediateDebitResponseDto(BaseModel):
    code: str = Field(..., examples=["ACCP"])
    """
    Network status code. Common values: `202` (OTP accepted), `ACCP` (accepted/completed), `AC00` (pending — gateway auto-polls), reject codes on failure.
    """
    message: Optional[str] = Field(None, examples=["Operación aceptada"])
    """
    Human-readable network message when provided.
    """
    reference: Optional[str] = Field(None, examples=["16142940"])
    """
    Bank reference when the operation settles synchronously.
    """
    id: Optional[str] = Field(None, examples=["6785d97e-2092-49f0-9f7d-3d5921f0b13f"])
    """
    Network operation id. Prefer this over `Id` when both are present. Use with GET /v1/payments/operations/:id.
    """
    Id: Optional[str] = Field(None, examples=["6785d97e-2092-49f0-9f7d-3d5921f0b13f"])
    """
    Alternate casing of the operation id some network responses use.
    """
    success: Optional[bool] = Field(None, examples=[True])
    """
    Present on some operation responses when the network returns an explicit success flag.
    """
    paymentId: str = Field(..., examples=["3fd84b2d-9ad1-4f74-a2d9-0f2f56984db5"])
    """
    VEXPay payment id for this débito inmediato (method DEBITO_INMEDIATO).
    """
    externalRef: Optional[str] = Field(
        None, examples=["fine_736a0b42-0b6e-454c-b87e-7f3c0e47057b"]
    )
    """
    Echo of the request externalRef when provided.
    """


class R4OperationResponseDto(BaseModel):
    code: str = Field(..., examples=["ACCP"])
    """
    Network status code. Common values: `202` (OTP accepted), `ACCP` (accepted/completed), `AC00` (pending — gateway auto-polls), reject codes on failure.
    """
    message: Optional[str] = Field(None, examples=["Operación aceptada"])
    """
    Human-readable network message when provided.
    """
    reference: Optional[str] = Field(None, examples=["16142940"])
    """
    Bank reference when the operation settles synchronously.
    """
    id: Optional[str] = Field(None, examples=["6785d97e-2092-49f0-9f7d-3d5921f0b13f"])
    """
    Network operation id. Prefer this over `Id` when both are present. Use with GET /v1/payments/operations/:id.
    """
    Id: Optional[str] = Field(None, examples=["6785d97e-2092-49f0-9f7d-3d5921f0b13f"])
    """
    Alternate casing of the operation id some network responses use.
    """
    success: Optional[bool] = Field(None, examples=[True])
    """
    Present on some operation responses when the network returns an explicit success flag.
    """


class Credit(BaseModel):
    telefono: str = Field(..., examples=["584121234567"])
    code: str = Field(..., examples=["ACCP"])
    reference: Optional[str] = Field(None, examples=["16142940"])
    id: Optional[str] = None


class CreditDisbursementResponseDto(BaseModel):
    paymentId: str
    """
    Id of the completed PAGO_MOVIL payment that funded this disbursement.
    """
    referencia: str = Field(..., examples=["12345678"])
    """
    Normalized bank reference used to locate the inbound payment.
    """
    credits: list[Credit]
    """
    Per-recipient credit results in request order.
    """


class AccountPayoutDispersionResponseDto(BaseModel):
    success: bool = Field(..., examples=[True])
    """
    Whether the bank network accepted the dispersion request.
    """
    message: Optional[str] = None
    """
    Network success message when provided.
    """
    error: Optional[str] = None
    """
    Network error detail when success is false.
    """
    referencia: str = Field(..., examples=["123456789"])
    """
    9-digit wire reference actually sent to the bank (last 9 digits of the request referencia).
    """


class ChangePaymentResponseDto(BaseModel):
    code: str = Field(..., examples=["ACCP"])
    """
    Network status code. Common values: `202` (OTP accepted), `ACCP` (accepted/completed), `AC00` (pending — gateway auto-polls), reject codes on failure.
    """
    message: Optional[str] = Field(None, examples=["Operación aceptada"])
    """
    Human-readable network message when provided.
    """
    reference: Optional[str] = Field(None, examples=["16142940"])
    """
    Bank reference when the operation settles synchronously.
    """
    id: Optional[str] = Field(None, examples=["6785d97e-2092-49f0-9f7d-3d5921f0b13f"])
    """
    Network operation id. Prefer this over `Id` when both are present. Use with GET /v1/payments/operations/:id.
    """
    Id: Optional[str] = Field(None, examples=["6785d97e-2092-49f0-9f7d-3d5921f0b13f"])
    """
    Alternate casing of the operation id some network responses use.
    """
    success: Optional[bool] = Field(None, examples=[True])
    """
    Present on some operation responses when the network returns an explicit success flag.
    """


class ManualOperationPollResponseDto(BaseModel):
    kind: Literal["debit", "payout", "verification_deposit"]
    id: str
    operationId: str
    """
    Network operation id that was polled.
    """
    statusBefore: str = Field(..., examples=["PENDING"])
    status: str = Field(..., examples=["COMPLETED"])
    failureCode: Optional[str] = None
    code: Optional[str] = Field(None, examples=["AC00"])
    """
    Latest network code from ConsultarOperaciones when available.
    """
    message: Optional[str] = None
    reference: Optional[str] = None


class GenerateDebitOtpDto(BaseModel):
    banco: str = Field(..., examples=["0191"], pattern="^\\d{3,4}$")
    """
    3–4 digit bank code (padded to 4 digits when sent to the network). Prefer codes from GET /v1/banks.
    """
    monto: float = Field(..., examples=[50], ge=0.01, le=1000000.0)
    """
    Debit amount in VES (not USD).
    """
    telefono: str = Field(..., examples=["584121234567"])
    """
    Payer mobile: 58 + 10 digits, or 0 + 10 digits local form.
    """
    cedula: str = Field(..., examples=["V12345678"])
    """
    Payer cédula/RIF (V/E/J/P/G + digits).
    """


class ImmediateDebitDto(BaseModel):
    banco: str = Field(..., examples=["0191"], pattern="^\\d{3,4}$")
    """
    3–4 digit bank code (padded to 4 digits when sent to the network). Prefer codes from GET /v1/banks.
    """
    monto: float = Field(..., examples=[50], ge=0.01, le=1000000.0)
    """
    Debit amount in VES (not USD).
    """
    telefono: str = Field(..., examples=["584121234567"])
    """
    Payer mobile: 58 + 10 digits, or 0 + 10 digits local form.
    """
    cedula: str = Field(..., examples=["V12345678"])
    """
    Payer cédula/RIF (V/E/J/P/G + digits).
    """
    nombre: str = Field(..., examples=["Maria Perez"], max_length=20)
    """
    Payer display name (max 20 chars, truncated for the bank).
    """
    otp: str = Field(..., examples=["123456"], pattern="^\\d{6,8}$")
    """
    OTP the payer bank SMS’d after POST /v1/payments/debit/otp.
    """
    concepto: str = Field(..., examples=["Pago de factura"], max_length=30)
    """
    Statement concept shown to the payer (max 30 chars).
    """
    externalRef: Optional[str] = Field(
        None, examples=["fine_736a0b42-0b6e-454c-b87e-7f3c0e47057b"], max_length=64
    )
    """
    Tenant correlation value for recovery lookup (GET /v1/payments/by-ref/:externalRef). Not an idempotency key; a ref that already has a COMPLETED payment is refused (409 external_ref_already_paid).
    """
    merchantId: Optional[str] = None
    applicationFeeVes: Optional[str] = Field(None, examples=["50.00"])
    """
    Marketplace application fee in VES retained by the platform.
    """
    applicationFeePercent: Optional[float] = Field(
        None, examples=[10], ge=0.0, le=100.0
    )
    """
    Optional percent of vesAmount used when applicationFeeVes is omitted. When both are omitted and merchantId is set, the merchant's commission (or the tenant default commission) applies.
    """


class ManualOperationPollDto(BaseModel):
    kind: Literal["debit", "payout", "verification_deposit"] = Field(
        ..., examples=["debit"]
    )
    """
    Which pending entity to reconcile.
    """
    id: str = Field(..., examples=["3fd84b2d-9ad1-4f74-a2d9-0f2f56984db5"])
    """
    Payment, payout, or verification deposit id (not the network operation id).
    """


class ImmediateCreditDto(BaseModel):
    banco: str = Field(..., examples=["0191"])
    """
    Beneficiary bank code (3–4 digits). Prefer codes from GET /v1/banks.
    """
    cedula: str = Field(..., examples=["V12345678"])
    """
    Beneficiary cédula/RIF.
    """
    telefono: str = Field(..., examples=["584121234567"])
    """
    Beneficiary Pago Móvil phone (58… or 0…).
    """
    monto: float = Field(..., examples=[50], ge=0.01, le=1000000.0)
    """
    Credit amount in VES.
    """
    concepto: str = Field(..., examples=["Pago de factura"], max_length=30)
    """
    Statement concept (max 30 chars).
    """


class AccountCreditDto(BaseModel):
    cedula: str = Field(..., examples=["V12345678"])
    """
    Account holder cédula/RIF.
    """
    cuenta: str = Field(
        ..., examples=["01910000000000000000"], max_length=20, min_length=20
    )
    """
    20-digit Venezuelan bank account number.
    """
    monto: float = Field(..., examples=[50])
    """
    Credit amount in VES.
    """
    concepto: str = Field(..., examples=["Pago de factura"], max_length=30)
    """
    Statement concept (max 30 chars).
    """


class CreditRecipientDto(BaseModel):
    banco: str = Field(..., examples=["0191"])
    """
    Recipient bank code (3–4 digits).
    """
    cedula: str = Field(..., examples=["V12345678"])
    """
    Recipient cédula/RIF.
    """
    telefono: str = Field(..., examples=["584121234567"])
    """
    Recipient Pago Móvil phone.
    """
    montoPart: float = Field(..., examples=[25])
    """
    Share of the total disbursement for this recipient (VES). Sum of montoPart must equal monto.
    """


class CreditDisbursementDto(BaseModel):
    monto: float = Field(..., examples=[50])
    """
    Total VES amount to disburse. Must match a completed PAGO_MOVIL payment’s vesAmount for the given referencia.
    """
    referencia: str = Field(..., examples=["123456789"])
    """
    Bank reference of a completed inbound Pago Móvil payment (up to 9 digits). Used to locate and mark that payment as dispersed.
    """
    concepto: str = Field(..., examples=["Dispersión"], max_length=30)
    """
    Concept applied to each credit leg.
    """
    personas: list[CreditRecipientDto]
    """
    One or more phone recipients. Sum of personas[].montoPart must equal monto.
    """


class PayoutRecipientDto(BaseModel):
    nombres: str = Field(..., examples=["Maria Perez"], max_length=80)
    """
    Beneficiary legal name.
    """
    documento: str = Field(..., examples=["V12345678"])
    """
    Beneficiary documento (V/E/J/P + digits).
    """
    destino: str = Field(
        ..., examples=["01910000000000000000"], max_length=20, min_length=20
    )
    """
    20-digit destination account number.
    """
    montoPart: float = Field(..., examples=[25])
    """
    Share for this beneficiary (VES). Sum of montoPart must equal monto.
    """


class PayoutDto(BaseModel):
    monto: float = Field(..., examples=[50])
    """
    Total VES amount across all personas.
    """
    fecha: str = Field(..., examples=["07/20/2026"], pattern="^\\d{2}/\\d{2}/\\d{4}$")
    """
    Value date as MM/DD/YYYY.
    """
    referencia: str = Field(..., examples=["123456789"])
    """
    Numeric reference (digits only). Only the last 9 digits are sent to the bank network.
    """
    personas: list[PayoutRecipientDto]
    """
    Account beneficiaries. Sum of personas[].montoPart must equal monto.
    """


class ChangePaymentDto(BaseModel):
    telefonoDestino: str = Field(..., examples=["584121234567"])
    """
    Customer phone that receives the change (vuelto).
    """
    cedula: str = Field(..., examples=["V12345678"])
    """
    Customer cédula/RIF.
    """
    banco: str = Field(..., examples=["0191"])
    """
    Customer bank code (3–4 digits).
    """
    monto: float = Field(..., examples=[5])
    """
    Change amount in VES.
    """
    concepto: Optional[str] = Field(None, examples=["Vuelto de compra"], max_length=30)
    """
    Optional statement concept (max 30 chars).
    """
    ip: Optional[str] = Field(None, examples=["203.0.113.10"], max_length=15)
    """
    Client IP recorded with the operation. Defaults to R4_DEFAULT_CLIENT_IP when omitted.
    """


class CryptoBalanceDto(BaseModel):
    currency: Literal["USDT", "USDC"] = Field(..., examples=["USDT"])
    available: str = Field(..., examples=["97.00"])
    """
    Available for payouts, in `currency` (ledger). Excludes `held`.
    """
    held: Optional[str] = Field(None, examples=["0.00"])
    """
    Under the 24h balance hold: credited but not payable until its hold ends, in `currency`.
    """
    nextReleaseAt: Optional[AwareDatetime] = None
    """
    When the soonest held amount becomes available; null when nothing is held.
    """
    pendingPayout: str = Field(..., examples=["50.10"])
    """
    Reserved by payouts that have not completed yet, in `currency`.
    """
    availableUsdt: Optional[str] = Field(None, examples=["97.00"])
    """
    USDT only: same as `available`.
    """
    pendingPayoutUsdt: Optional[str] = Field(None, examples=["50.10"])
    """
    USDT only: same as `pendingPayout`.
    """
    heldUsdt: Optional[str] = Field(None, examples=["0.00"])
    """
    USDT only: same as `held`.
    """
    asOf: AwareDatetime


class CryptoBalancesDto(BaseModel):
    data: list[CryptoBalanceDto]
    """
    One balance per stablecoin (USDT, USDC).
    """


class CreateDepositAddressDto(BaseModel):
    customerRef: str = Field(..., examples=["user_123"])
    """
    Your identifier for the customer this address belongs to (1–128 chars: A–Z a–z 0–9 _ . : @ -).
    """
    network: Literal["TRC20", "BEP20", "POLYGON", "SOL", "TON", "ARB1", "BASE"] = Field(
        ..., examples=["BEP20"]
    )
    """
    USDT: TRC20, BEP20, POLYGON, SOL, TON, ARB1. USDC: POLYGON, BASE.
    """
    currency: Literal["USDT", "USDC"] = Field("USDT", examples=["USDT"])
    """
    Stablecoin the address receives.
    """


class DepositAddressDto(BaseModel):
    customerRef: str = Field(..., examples=["user_123"])
    network: str = Field(..., examples=["BEP20"])
    currency: Literal["USDT", "USDC"] = Field(..., examples=["USDT"])
    address: str = Field(..., examples=["0x9f3c…"])
    tag: Optional[str] = None
    """
    Destination tag / memo the payer must include (TON).
    """
    tagRequired: bool
    """
    True when the network requires the tag.
    """
    createdAt: AwareDatetime


class SimulateDepositDto(BaseModel):
    customerRef: str = Field(..., examples=["user_123"])
    """
    The `customerRef` of a deposit address you already requested.
    """
    network: Literal["TRC20", "BEP20", "POLYGON", "SOL", "TON", "ARB1", "BASE"] = Field(
        ..., examples=["TRC20"]
    )
    """
    Network of that deposit address.
    """
    currency: Literal["USDT", "USDC"] = Field("USDT", examples=["USDT"])
    """
    Stablecoin of that deposit address.
    """
    amount: Union[str, float] = Field(..., examples=["40.00"])
    """
    Amount that "arrives", in `currency`: greater than 0, at most 10,000, at most 2 decimals.
    """


class SimulatedDepositDto(BaseModel):
    paymentId: str
    status: Literal["COMPLETED"] = Field(..., examples=["COMPLETED"])
    method: Literal["USDT", "USDC"] = Field(..., examples=["USDT"])
    currency: Literal["USDT", "USDC"] = Field(..., examples=["USDT"])
    amount: str = Field(..., examples=["40.00"])
    """
    Amount received, in `currency`.
    """
    fee: str = Field(..., examples=["1.50"])
    """
    Your stablecoin fee, in `currency`. The balance is credited `amount` − `fee`.
    """
    amountUsdt: Optional[str] = Field(None, examples=["40.00"])
    """
    USDT only: same as `amount`.
    """
    feeUsdt: Optional[str] = Field(None, examples=["1.50"])
    """
    USDT only: same as `fee`.
    """
    network: str = Field(..., examples=["TRC20"])
    customerRef: str = Field(..., examples=["user_123"])
    txHashes: list[str] = Field(..., examples=[[]])
    """
    Always empty: nothing moved on chain.
    """
    livemode: bool = Field(..., examples=[False])
    """
    Always false: simulated deposits exist in Test mode only.
    """
    simulated: bool = Field(..., examples=[True])
    createdAt: AwareDatetime


class CryptoNetworkDto(BaseModel):
    currency: Literal["USDT", "USDC"] = Field(..., examples=["USDT"])
    network: str = Field(..., examples=["POLYGON"])
    displayName: str = Field(..., examples=["Polygon"])
    receiveEnabled: bool
    payoutEnabled: bool
    payoutFee: str = Field(..., examples=["0.10"])
    """
    Payout fee in `currency`.
    """
    minPayout: str = Field(..., examples=["1.00"])
    """
    Minimum payout in `currency`.
    """
    payoutFeeUsdt: Optional[str] = Field(None, examples=["0.10"])
    """
    USDT only: same as `payoutFee`.
    """
    minPayoutUsdt: Optional[str] = Field(None, examples=["1.00"])
    """
    USDT only: same as `minPayout`.
    """
    tagRequired: bool
    available: bool
    """
    Whether a payout of the requested amount can be sent on this network now.
    """


class CreateCryptoPayoutDto(BaseModel):
    currency: Literal["USDT", "USDC"] = Field("USDT", examples=["USDT"])
    """
    Stablecoin to send; debits that balance.
    """
    network: Literal["TRC20", "BEP20", "POLYGON", "SOL", "TON", "ARB1", "BASE"] = Field(
        ..., examples=["POLYGON"]
    )
    """
    USDT: TRC20, BEP20, POLYGON, SOL, TON, ARB1. USDC: POLYGON, BASE.
    """
    address: str = Field(..., examples=["0x9f3c4e1b2a7d6c5e4f3a2b1c0d9e8f7a6b5c4d3e"])
    tag: Optional[str] = None
    """
    Destination tag / memo (required on TON).
    """
    amount: Optional[str] = Field(None, examples=["50.00"])
    """
    Amount the destination receives, in `currency` (max 2 decimals).
    """
    amountUsdt: Optional[str] = Field(None, examples=["50.00"])
    """
    USDT only: alias of `amount`.
    """
    customerRef: Optional[str] = Field(None, examples=["user_123"])
    """
    Your customer reference, echoed on webhooks.
    """
    idempotencyKey: str = Field(..., examples=["withdrawal_8812"])
    """
    Unique per payout. Replays return the same payout (200).
    """


class CryptoPayoutDto(BaseModel):
    id: str
    object: str = Field(..., examples=["crypto.payout"])
    currency: Literal["USDT", "USDC"] = Field(..., examples=["USDT"])
    status: Literal["pending", "processing", "completed", "failed"]
    network: str
    address: str
    tag: Optional[str] = None
    amount: str = Field(..., examples=["50.00"])
    """
    Amount sent, in `currency`.
    """
    fee: str = Field(..., examples=["0.10"])
    """
    Network fee + margin, in `currency` (0 for internal).
    """
    amountUsdt: Optional[str] = Field(None, examples=["50.00"])
    """
    USDT only: same as `amount`.
    """
    feeUsdt: Optional[str] = Field(None, examples=["0.10"])
    """
    USDT only: same as `fee`.
    """
    customerRef: Optional[str] = None
    merchantId: Optional[str] = None
    idempotencyKey: str
    txHash: Optional[str] = None
    internal: bool
    """
    Settled inside VEXPay (destination is one of your own deposit addresses).
    """
    failureReason: Optional[str] = None
    createdAt: AwareDatetime
    completedAt: Optional[AwareDatetime] = None


class CopChannelDto(BaseModel):
    channel: Literal[
        "breb",
        "nequi",
        "daviplata",
        "card",
        "pse",
        "bancolombia_transfer",
        "bancolombia_qr",
    ] = Field(..., examples=["pse"])
    label: str = Field(..., examples=["PSE"])
    """
    Buyer-facing name (Spanish).
    """
    needsBuyer: bool = Field(..., examples=[True])
    """
    A `buyer` object is required.
    """
    needsTermsAcceptance: bool = Field(..., examples=[True])
    """
    Show the buyer the `terms` links and send `buyer.termsAccepted: true`.
    """
    checkoutOnly: bool = Field(..., examples=[False])
    """
    Only through the hosted checkout (checkout sessions or payment links), never `POST /v1/cop/payments`.
    """
    minAmountCop: float = Field(..., examples=[20000])


class CopPseBankDto(BaseModel):
    code: str = Field(..., examples=["1007"])
    name: str = Field(..., examples=["Bancolombia"])


class CopTermsDto(BaseModel):
    termsUrl: str
    """
    Terms and conditions the buyer accepts.
    """
    personalDataUrl: str
    """
    Personal data processing authorization the buyer accepts.
    """


class CopChannelsDto(BaseModel):
    channels: list[CopChannelDto]
    pseBanks: Optional[list[CopPseBankDto]] = None
    """
    Present when `pse` is listed: banks for `pse.bankCode`.
    """
    terms: Optional[CopTermsDto] = None
    """
    Present when a listed channel needs terms acceptance.
    """


class CopBuyerDto(BaseModel):
    firstName: Optional[str] = Field(None, examples=["Juan"], max_length=50)
    lastName: Optional[str] = Field(None, examples=["Pérez"], max_length=50)
    email: Optional[str] = Field(None, examples=["juan@example.com"])
    """
    Required for every channel except `breb`.
    """
    phone: Optional[str] = Field(None, examples=["3001234567"])
    """
    Colombian mobile number (10 digits starting with 3, with or without +57). Required for Nequi (it receives the push) and Daviplata.
    """
    documentType: Optional[Literal["CC", "CE", "TI", "NIT", "PP"]] = Field(
        None, examples=["CC"]
    )
    """
    Required for Nequi and Daviplata. Daviplata accepts CC, CE and TI only.
    """
    documentNumber: Optional[str] = Field(None, examples=["1234567890"])
    """
    National document number. Required for every channel except `breb`.
    """
    personType: Optional[Literal["natural", "juridica"]] = Field(
        None, examples=["natural"]
    )
    """
    PSE only (required): `natural` person or `juridica` (company).
    """
    termsAccepted: Optional[bool] = Field(None, examples=[True])
    """
    Required (`true`) for channels the channel catalog marks `needsTermsAcceptance`: confirms you showed the buyer the catalog `terms` links.
    """


class CopPseDto(BaseModel):
    bankCode: str = Field(..., examples=["1007"])
    """
    Bank code from `GET /v1/cop/channels` → `pseBanks`.
    """


class CreateCopPaymentDto(BaseModel):
    amountCop: float = Field(..., examples=[100000], ge=2000.0)
    """
    Amount in whole Colombian pesos. At least 2,000 (`amount_below_minimum` otherwise).
    """
    channel: Literal[
        "breb",
        "nequi",
        "daviplata",
        "card",
        "pse",
        "bancolombia_transfer",
        "bancolombia_qr",
    ] = Field(..., examples=["breb"])
    """
    `breb`: QR code / transfer key the buyer pays from any Colombian bank app. `nequi`: push to the buyer's Nequi app. `daviplata`: SMS code the buyer reads to you, or a redirect. `pse` and `bancolombia_transfer`: redirect to the buyer's bank. `bancolombia_qr`: QR the buyer scans in the Bancolombia app. `card`: hosted checkout only (`channel_requires_checkout`).
    """
    description: Optional[str] = Field(None, examples=["Order 1042"], max_length=255)
    """
    Shown to the buyer.
    """
    reference: Optional[str] = Field(None, examples=["order-1042"], max_length=64)
    """
    Your reference, echoed in reads and webhooks.
    """
    metadata: Optional[dict[str, str]] = Field(None, examples=[{"orderId": "1042"}])
    """
    Up to 20 string key/value pairs (keys ≤ 40 chars, values ≤ 500 chars).
    """
    buyer: Optional[CopBuyerDto] = None
    """
    Required for every channel except `breb`.
    """
    pse: Optional[CopPseDto] = None
    """
    Required for `pse`.
    """


class CopNextActionDto(BaseModel):
    type: Literal[
        "show_qr",
        "approve_in_app",
        "submit_otp",
        "redirect",
        "redirect_pending",
        "processing",
    ]
    """
    `redirect`: send the buyer to `url` to authorize at their bank. `redirect_pending`: the URL is not ready yet — read the payment again. `processing`: nothing to do, the outcome follows.
    """
    qrPngBase64: Optional[str] = None
    """
    Bre-B: base64 PNG of the payment QR. Returned only when the payment is created.
    """
    qrSvgBase64: Optional[str] = None
    """
    Bancolombia QR: base64 SVG of the payment QR.
    """
    url: Optional[str] = Field(None, examples=["https://…"])
    """
    `redirect`: where the buyer authorizes the payment.
    """
    transferKey: Optional[str] = None
    """
    Bre-B: transfer key the buyer can enter instead of scanning.
    """
    phoneMasked: Optional[str] = Field(None, examples=["****567"])
    """
    Nequi: masked phone that received the push.
    """


class CopPaymentDto(BaseModel):
    id: str
    status: Literal["pending", "completed", "failed", "canceled", "refunded"]
    method: Literal["COP"]
    channel: Literal[
        "breb",
        "nequi",
        "daviplata",
        "card",
        "pse",
        "bancolombia_transfer",
        "bancolombia_qr",
    ]
    amountCop: float = Field(..., examples=[100000])
    feeCop: Optional[float] = Field(None, examples=[3500])
    """
    Present once completed.
    """
    amountUsd: Optional[str] = Field(None, examples=["5.00"])
    """
    Hosted checkout payments only: the USD price the peso amount was computed from.
    """
    copRate: Optional[str] = Field(None, examples=["3316.382375"])
    """
    Hosted checkout payments only: COP per USD the buyer was charged at.
    """
    reference: Optional[str] = Field(None, examples=["order-1042"])
    metadata: dict[str, str]
    failureCode: Optional[
        Literal[
            "expired", "rejected", "processor_error", "processor_unknown", "chargeback"
        ]
    ] = None
    """
    `chargeback`: a refunded card payment the buyer disputed with their bank.
    """
    expiresAt: Optional[AwareDatetime] = None
    createdAt: AwareDatetime
    completedAt: Optional[AwareDatetime] = None
    next: Optional[CopNextActionDto] = None
    """
    What the buyer must do next. Returned when the payment is created, and on reads while a bank redirect or QR is pending.
    """
    card: Optional[dict[str, Any]] = Field(
        None, examples=[{"brand": "VISA", "last4": "4242"}]
    )
    """
    Card payments: brand and last 4 digits, once known.
    """


class SubmitCopOtpDto(BaseModel):
    otp: str = Field(..., examples=["123456"])
    """
    The code the buyer received by SMS.
    """


class CopBalanceDto(BaseModel):
    availableCop: float = Field(..., examples=[96500])
    """
    Whole pesos available for payout. Excludes `heldCop`.
    """
    heldCop: Optional[float] = Field(None, examples=[0])
    """
    Whole pesos under the 24h balance hold: credited but not payable until the hold ends.
    """
    nextReleaseAt: Optional[AwareDatetime] = None
    """
    When the soonest held amount becomes available; null when nothing is held.
    """
    pendingPayoutCop: float = Field(..., examples=[0])
    """
    Whole pesos reserved by payouts in progress.
    """
    asOf: AwareDatetime


class CurrencyFlagsDto(BaseModel):
    VES: bool
    COP: bool


class CurrencyAmountsDto(BaseModel):
    VES: str = Field(..., examples=["3.0000"])
    COP: str = Field(..., examples=["3.0000"])


class CurrencyCapsDto(BaseModel):
    VES: Optional[str] = Field(..., examples=[None])
    """
    Max VES per Caracas day; `null` = no cap.
    """
    COP: Optional[str] = Field(..., examples=["2000000"])
    """
    Max COP per Bogotá day; `null` = no cap.
    """


class AutoConvertPercentDto(BaseModel):
    percent: int = Field(..., examples=[50], ge=0, le=100)
    """
    Whole number; 0 = off.
    """


class AutoConvertDto(BaseModel):
    COP: AutoConvertPercentDto


class ConversionSettingsDto(BaseModel):
    object: str = Field(..., examples=["conversion_settings"])
    enabled: bool
    """
    Conversions are enabled for your account.
    """
    sourceCurrencies: CurrencyFlagsDto
    """
    Which currencies you can convert from right now.
    """
    spreadPercent: CurrencyAmountsDto
    """
    Your spread per source currency, in percent.
    """
    minimumUsdt: str = Field(..., examples=["10.00"])
    """
    Smallest USDT amount a conversion may deliver.
    """
    dailyMax: CurrencyCapsDto
    autoConvert: AutoConvertDto


class UpdateConversionSettingsDto(BaseModel):
    autoConvert: AutoConvertDto = Field(..., examples=[{"COP": {"percent": 50}}])


class CreateConversionQuoteDto(BaseModel):
    sourceCurrency: Literal["VES", "COP"] = "VES"
    """
    Currency you convert from. Defaults to `VES`.
    """
    sourceAmount: Optional[str] = Field(None, examples=["1000000"])
    """
    Amount of `sourceCurrency` to spend (VES: up to 2 decimals; COP: whole pesos). Send this or `targetAmountUsdt`, not both.
    """
    sourceAmountVes: Optional[str] = Field(None, examples=["10000.00"])
    """
    VES only: same as `sourceAmount` (kept for existing integrations).
    """
    targetAmountUsdt: Optional[str] = Field(None, examples=["50.00"])
    """
    USDT to receive. Send this or `sourceAmount`, not both.
    """


class ConversionQuoteDto(BaseModel):
    id: str
    object: str = Field(..., examples=["conversion_quote"])
    rate: str = Field(..., examples=["998.8299"])
    """
    Units of `sourceCurrency` per 1 USDT you get: market rate plus your spread.
    """
    marketRate: str = Field(..., examples=["979.2450"])
    """
    Market USDT rate (in `sourceCurrency`) the quote is based on.
    """
    spreadPercent: str = Field(..., examples=["2.0000"])
    """
    Your spread, in percent.
    """
    rateSource: Literal["market"] = Field(..., examples=["market"])
    sourceCurrency: Literal["VES", "COP"]
    sourceAmount: str = Field(..., examples=["10000.00"])
    """
    Amount debited (VES to the cent, COP in whole pesos; rounded up).
    """
    sourceAmountVes: Optional[str] = Field(..., examples=["10000.00"])
    """
    VES quotes only; `null` for COP.
    """
    targetAmountUsdt: str = Field(..., examples=["10.01"])
    """
    Rounded down to the cent.
    """
    expiresAt: str
    """
    The quote can be accepted until this time (60 seconds).
    """
    createdAt: str


class CreateConversionDto(BaseModel):
    quoteId: str
    """
    A live quote from `POST /v1/conversions/quotes`. Each quote can be used once.
    """
    reference: Optional[str] = Field(None, examples=["treasury-2026-10-03"])
    """
    Your reference, echoed on the conversion and its webhooks.
    """


class ConversionDto(BaseModel):
    id: str
    object: str = Field(..., examples=["conversion"])
    status: Literal["PENDING", "COMPLETED", "CANCELED"]
    reference: Optional[str] = Field(...)
    rate: str = Field(..., examples=["998.8299"])
    marketRate: str = Field(..., examples=["979.2450"])
    spreadPercent: str = Field(..., examples=["2.0000"])
    rateSource: Literal["market"] = Field(..., examples=["market"])
    sourceCurrency: Literal["VES", "COP"]
    sourceAmount: str = Field(..., examples=["10000.00"])
    """
    Amount debited (VES to the cent, COP in whole pesos).
    """
    sourceAmountVes: Optional[str] = Field(..., examples=["10000.00"])
    """
    VES conversions only; `null` for COP.
    """
    targetAmountUsdt: str = Field(..., examples=["10.01"])
    origin: Literal["api", "auto"]
    """
    `auto` when created by auto-convert from a pay-in.
    """
    paymentId: Optional[str] = Field(...)
    """
    The pay-in an auto-conversion came from; `null` otherwise.
    """
    createdAt: str
    completedAt: Optional[str] = Field(...)
    canceledAt: Optional[str] = Field(...)
    cancelReason: Optional[str] = Field(...)


class ConversionListDto(BaseModel):
    items: list[ConversionDto]
    nextCursor: Optional[str] = Field(...)
    """
    Pass as `cursor` to get the next page.
    """


class BankResponseDto(BaseModel):
    code: str = Field(..., examples=["0102"])
    """
    Canonical four-digit SIMF bank code.
    """
    name: str = Field(..., examples=["Banco de Venezuela"])
    services: list[str]
    """
    Provider-reported services; may be empty.
    """
    logoUrl: Optional[str] = Field(
        ..., examples=["https://pub-xxxxx.r2.dev/vebanking/banks/0102.png"]
    )
    """
    Public URL for a 100×100 bank logo image (PNG), or null when not uploaded. Render this next to the bank name in selectors so users can identify their bank quickly.
    """


class QuoteResponseDto(BaseModel):
    usdAmount: float = Field(..., examples=[25])
    bcvRate: float = Field(..., examples=[36.5])
    """
    Official VEX FX BCV rate (Bs per $1).
    """
    rate: Optional[float] = Field(None, examples=[36.5])
    """
    Rate your payments are priced at (Bs per $1): `bcvRate` for BCV accounts, the market rate for MARKET accounts.
    """
    rateSource: Optional[Literal["BCV", "MARKET"]] = Field(None, examples=["BCV"])
    """
    Your account's Bolívar rate setting.
    """
    vesAmount: float = Field(..., examples=[912.5])
    """
    usdAmount × rate, rounded to the cent: what a payment created now would charge.
    """
    medianRate: float = Field(..., examples=[36.55])
    """
    Median of available BCV sources (VEX FX + bank)
    """
    medianVesAmount: float = Field(..., examples=[913.75])
    """
    USD amount converted at medianRate
    """
    source: str = Field(..., examples=["bcv"])
    fetchedAt: AwareDatetime
    sources: dict[str, Any] = Field(
        ...,
        examples=[
            {
                "vexFx": {"rate": 36.5, "fetchedAt": "2026-07-23T12:00:00.000Z"},
                "bank": {"rate": 36.6, "fetchedAt": "2026-07-23T12:00:00.000Z"},
            }
        ],
    )
    """
    Per-source BCV rates or error objects (e.g. `{ error: "BANK_NOT_CONFIGURED" }`). Keys typically include `vexFx` and `bank`. `sources.bank` is the partner-bank BCV rate when available.
    """


class OnwardPayoutDto(BaseModel):
    network: str = Field(..., examples=["BEP20"])
    """
    USDT payout network (see GET /v1/crypto/networks).
    """
    address: str = Field(..., examples=["0x2f5c…"])
    """
    Destination wallet address. Only its format is checked: a wrong but valid address cannot be recovered.
    """
    tag: Optional[str] = None
    """
    Destination tag / memo, for networks that need one (e.g. TON).
    """


class C2pRequestDto(BaseModel):
    usdAmount: Optional[float] = Field(None, examples=[25], ge=0.01, le=100000.0)
    """
    USD amount. Required unless vesAmount is set. When only usdAmount is set, VES is derived at your Bolívar rate (live BCV, or market if you chose it).
    """
    vesAmount: Optional[float] = Field(None, examples=[50], ge=0.01, le=100000000.0)
    """
    VES amount debited at the bank. When set, locks the bolívar charge and derives USD at your Bolívar rate (it wins over usdAmount). The intent keeps this amount until it is executed.
    """
    debtorId: str = Field(..., examples=["V12345678"])
    debtorCellPhone: str = Field(..., examples=["584121234567"])
    """
    Country code 58 followed by 10 digits.
    """
    debtorBankCode: float = Field(..., examples=[102])
    """
    Venezuelan bank institution code (e.g. 102, 105, 134). Must match a bank from GET /v1/banks.
    """
    externalRef: Optional[str] = Field(None, examples=["order-1042"], max_length=64)
    """
    Correlation value; not an idempotency key. A ref that already has a COMPLETED payment is refused (409 external_ref_already_paid). When present, any other PENDING C2P intent for this tenant + externalRef is canceled (superseded) before the new intent is created.
    """
    merchantId: Optional[str] = None
    applicationFeeVes: Optional[str] = Field(None, examples=["50.00"])
    """
    Marketplace application fee in VES retained by the platform.
    """
    applicationFeePercent: Optional[float] = Field(
        None, examples=[10], ge=0.0, le=100.0
    )
    """
    Optional percent of vesAmount used when applicationFeeVes is omitted. When both are omitted and merchantId is set, the merchant's commission (or the tenant default commission) applies.
    """
    onwardPayout: Optional[OnwardPayoutDto] = None
    """
    Convert this payment's net VES to USDT once it completes and send it to this wallet. Needs USDT and conversions enabled; not allowed with merchantId. See the "Pay in bolívars, receive USDT" guide.
    """


class OnwardPayoutStatusDto(BaseModel):
    status: Literal[
        "pending",
        "converting",
        "waiting_release",
        "sending",
        "completed",
        "held",
        "failed",
        "canceled",
    ] = Field(..., examples=["completed"])
    """
    `waiting_release`: converted, waiting for the 24h balance hold to end before sending (see `sendAfter`).
    """
    network: str = Field(..., examples=["BEP20"])
    address: str = Field(..., examples=["0x2f5c0000000000000000000000000000000000aa"])
    tag: Optional[str] = None
    conversionId: Optional[str] = None
    """
    The VES → USDT conversion, once created.
    """
    payoutId: Optional[str] = None
    """
    The USDT payout, once created.
    """
    amountUsdt: Optional[str] = Field(None, examples=["18.94"])
    """
    USDT sent to the address.
    """
    feeUsdt: Optional[str] = Field(None, examples=["0.75"])
    """
    Network payout fee.
    """
    txHash: Optional[str] = None
    """
    On-chain hash once the payout completed.
    """
    reason: Optional[str] = Field(None, examples=["below_payout_minimum"])
    """
    Why it is held, failed or canceled.
    """
    sendAfter: Optional[AwareDatetime] = None
    """
    `waiting_release` only: when the converted USDT leaves the balance hold and the payout is sent.
    """
    updatedAt: AwareDatetime


class C2pIntentResponseDto(BaseModel):
    paymentId: str = Field(..., examples=["3fd84b2d-9ad1-4f74-a2d9-0f2f56984db5"])
    externalRef: Optional[str] = Field(None, examples=["order-1042"])
    """
    Tenant correlation value; not an idempotency key.
    """
    status: Literal["PENDING", "COMPLETED", "FAILED", "CANCELED", "REVERSED"]
    method: Literal["C2P", "VPOS", "PAGO_MOVIL", "DEBITO_INMEDIATO"]
    usdAmount: float = Field(..., examples=[25])
    vesAmount: float = Field(..., examples=[912.5])
    bcvRate: float = Field(..., examples=[36.5])
    """
    Official BCV rate (Bs per $1) when the payment was created. Reference only; see `rate`.
    """
    rate: Optional[float] = Field(None, examples=[36.5])
    """
    Rate (Bs per $1) this payment was priced at: equal to `bcvRate` for BCV tenants, the market rate for MARKET tenants.
    """
    rateSource: Optional[Literal["BCV", "MARKET"]] = Field(None, examples=["BCV"])
    """
    Source of `rate`: the account's Bolívar rate setting when the payment was created.
    """
    feeUsd: Optional[float] = Field(None, examples=[0.88])
    """
    Platform service fee, USD. Clamped 0..usdAmount.
    """
    feeVes: Optional[float] = Field(None, examples=[32.12])
    """
    Platform service fee, VES. Clamped 0..vesAmount.
    """
    netVes: Optional[float] = Field(None, examples=[880.38])
    """
    What the seller receives: vesAmount − platform fee − application fee, floored at 0.
    """
    bankReference: Optional[str] = Field(None, examples=["00512673"])
    bankTxId: Optional[float] = Field(None, examples=[842901])
    debtorId: Optional[str] = Field(None, examples=["V12345678"])
    debtorPhone: Optional[str] = Field(None, examples=["584121234567"])
    debtorBankCode: Optional[float] = Field(None, examples=[102])
    debtorBankName: Optional[str] = Field(None, examples=["Banco de Venezuela"])
    cardLast4: Optional[str] = Field(None, examples=["4242"])
    cardBrand: Optional[str] = Field(None, examples=["Visa"])
    cardProduct: Optional[str] = Field(None, examples=["Crédito"])
    accountTypeLabel: Optional[str] = Field(None, examples=["Cuenta corriente"])
    tenantName: str = Field(..., examples=["Comercio Demo"])
    createdAt: AwareDatetime
    failureCode: Optional[str] = Field(None, examples=["MOVEMENT_NOT_FOUND"])
    cancelReason: Optional[Literal["superseded", "expired"]] = None
    """
    Present when status is CANCELED. superseded = replaced by a newer intent; expired = abandoned after TTL.
    """
    reversedAt: Optional[AwareDatetime] = None
    reversalRef: Optional[str] = Field(None, examples=["00991420"])
    reversalTxId: Optional[float] = Field(None, examples=[842950])
    onwardPayout: Optional[OnwardPayoutStatusDto] = None
    """
    Present when the pay-in was sent with `onwardPayout`.
    """
    intentId: str
    """
    Use this value as intentId when executing the C2P charge.
    """
    otpRequested: bool
    """
    true when the provider instructed the payer bank to SMS an OTP to the customer. false when the customer must generate the token in their bank app.
    """


class C2pPaymentDto(BaseModel):
    intentId: Optional[str] = None
    """
    Pending intent returned by POST /v1/payments/c2p/request.
    """
    usdAmount: Optional[float] = Field(None, examples=[25], ge=0.01, le=100000.0)
    """
    USD amount. Required unless vesAmount or intentId is set. When only usdAmount is set, VES is derived at your Bolívar rate (live BCV, or market if you chose it).
    """
    vesAmount: Optional[float] = Field(None, examples=[50], ge=0.01, le=100000000.0)
    """
    VES amount debited at the bank. When set, locks the bolívar charge and derives USD at your Bolívar rate (it wins over usdAmount). With intentId the amount locked on the intent is charged; amounts sent here must match it (±0.01 Bs / ±$0.01).
    """
    debtorId: str = Field(..., examples=["V12345678"])
    debtorCellPhone: str = Field(..., examples=["584121234567"])
    debtorBankCode: float = Field(..., examples=[102])
    """
    Venezuelan bank institution code (e.g. 102, 105, 134). Must match a bank from GET /v1/banks.
    """
    token: str = Field(..., examples=["123456"], pattern="^\\d{6,8}$")
    """
    Bank-issued token collected by the tenant from the customer.
    """
    externalRef: Optional[str] = Field(None, examples=["order-1042"], max_length=64)
    """
    Correlation value; not an idempotency key. A ref that already has a COMPLETED payment is refused (409 external_ref_already_paid).
    """
    merchantId: Optional[str] = None
    """
    Seller merchant to auto-credit on payment.completed (net = ves − plan fee − applicationFee).
    """
    applicationFeeVes: Optional[str] = Field(None, examples=["50.00"])
    """
    Marketplace application fee in VES retained by the platform.
    """
    applicationFeePercent: Optional[float] = Field(
        None, examples=[10], ge=0.0, le=100.0
    )
    """
    Optional percent of vesAmount used when applicationFeeVes is omitted. When both are omitted and merchantId is set, the merchant's commission (or the tenant default commission) applies.
    """
    onwardPayout: Optional[OnwardPayoutDto] = None
    """
    Convert this payment's net VES to USDT once it completes and send it to this wallet. Needs USDT and conversions enabled; not allowed with merchantId. See the "Pay in bolívars, receive USDT" guide.
    """


class PaymentReceiptDto(BaseModel):
    paymentId: str = Field(..., examples=["3fd84b2d-9ad1-4f74-a2d9-0f2f56984db5"])
    externalRef: Optional[str] = Field(None, examples=["order-1042"])
    """
    Tenant correlation value; not an idempotency key.
    """
    status: Literal["PENDING", "COMPLETED", "FAILED", "CANCELED", "REVERSED"]
    method: Literal["C2P", "VPOS", "PAGO_MOVIL", "DEBITO_INMEDIATO"]
    usdAmount: float = Field(..., examples=[25])
    vesAmount: float = Field(..., examples=[912.5])
    bcvRate: float = Field(..., examples=[36.5])
    """
    Official BCV rate (Bs per $1) when the payment was created. Reference only; see `rate`.
    """
    rate: Optional[float] = Field(None, examples=[36.5])
    """
    Rate (Bs per $1) this payment was priced at: equal to `bcvRate` for BCV tenants, the market rate for MARKET tenants.
    """
    rateSource: Optional[Literal["BCV", "MARKET"]] = Field(None, examples=["BCV"])
    """
    Source of `rate`: the account's Bolívar rate setting when the payment was created.
    """
    feeUsd: Optional[float] = Field(None, examples=[0.88])
    """
    Platform service fee, USD. Clamped 0..usdAmount.
    """
    feeVes: Optional[float] = Field(None, examples=[32.12])
    """
    Platform service fee, VES. Clamped 0..vesAmount.
    """
    netVes: Optional[float] = Field(None, examples=[880.38])
    """
    What the seller receives: vesAmount − platform fee − application fee, floored at 0.
    """
    bankReference: Optional[str] = Field(None, examples=["00512673"])
    bankTxId: Optional[float] = Field(None, examples=[842901])
    debtorId: Optional[str] = Field(None, examples=["V12345678"])
    debtorPhone: Optional[str] = Field(None, examples=["584121234567"])
    debtorBankCode: Optional[float] = Field(None, examples=[102])
    debtorBankName: Optional[str] = Field(None, examples=["Banco de Venezuela"])
    cardLast4: Optional[str] = Field(None, examples=["4242"])
    cardBrand: Optional[str] = Field(None, examples=["Visa"])
    cardProduct: Optional[str] = Field(None, examples=["Crédito"])
    accountTypeLabel: Optional[str] = Field(None, examples=["Cuenta corriente"])
    tenantName: str = Field(..., examples=["Comercio Demo"])
    createdAt: AwareDatetime
    failureCode: Optional[str] = Field(None, examples=["MOVEMENT_NOT_FOUND"])
    cancelReason: Optional[Literal["superseded", "expired"]] = None
    """
    Present when status is CANCELED. superseded = replaced by a newer intent; expired = abandoned after TTL.
    """
    reversedAt: Optional[AwareDatetime] = None
    reversalRef: Optional[str] = Field(None, examples=["00991420"])
    reversalTxId: Optional[float] = Field(None, examples=[842950])
    onwardPayout: Optional[OnwardPayoutStatusDto] = None
    """
    Present when the pay-in was sent with `onwardPayout`.
    """


class VposPaymentDto(BaseModel):
    usdAmount: Optional[float] = Field(None, examples=[25], ge=0.01, le=100000.0)
    """
    USD amount. Required unless vesAmount is set. When only usdAmount is set, VES is derived at your Bolívar rate (live BCV, or market if you chose it).
    """
    vesAmount: Optional[float] = Field(None, examples=[50], ge=0.01, le=100000000.0)
    """
    VES amount charged at the bank. When set, locks the bolívar charge and derives USD at your Bolívar rate — use this to avoid USD↔VES 2-decimal round-trip drift (e.g. Bs. 50 → $0.07 → Bs. 52.86).
    """
    cardNumber: str = Field(..., examples=["4111111111111111"], pattern="^\\d{13,19}$")
    """
    Handle only in a PCI-compliant server environment.
    """
    expirationMonth: float = Field(..., examples=[12], ge=1.0, le=12.0)
    expirationYear: float = Field(..., examples=[2028], ge=2020.0, le=2099.0)
    cvv: str = Field(..., examples=["123"], pattern="^\\d{3,4}$")
    cardPin: Optional[str] = Field(None, examples=["1234"], pattern="^\\d{4}$")
    """
    Card PIN (4 digits). Optional; defaults to 0000 when omitted.
    """
    cardHolderName: str = Field(
        ..., examples=["Maria Perez"], max_length=80, min_length=2
    )
    cardHolderId: str = Field(..., examples=["V12345678"])
    accountType: Literal[0, 10, 20] = Field(..., examples=[0])
    """
    0 credit, 10 savings, 20 checking.
    """
    cardType: Literal[1, 2, 3] = Field(..., examples=[1])
    """
    Provider card-brand code.
    """
    externalRef: Optional[str] = Field(None, examples=["order-1042"], max_length=64)
    """
    Correlation value; not an idempotency key. A ref that already has a COMPLETED payment is refused (409 external_ref_already_paid).
    """
    beneficiary: Optional[str] = Field(None, examples=["@maria"], max_length=80)
    """
    Who the funds are for when that is not a merchant (e.g. the wallet user being topped up). Shown to ops only; does not affect settlement.
    """
    merchantId: Optional[str] = None
    applicationFeeVes: Optional[str] = Field(None, examples=["50.00"])
    """
    Marketplace application fee in VES retained by the platform.
    """
    applicationFeePercent: Optional[float] = Field(
        None, examples=[10], ge=0.0, le=100.0
    )
    """
    Optional percent of vesAmount used when applicationFeeVes is omitted. When both are omitted and merchantId is set, the merchant's commission (or the tenant default commission) applies.
    """


class PaymentMethodAvailabilityDto(BaseModel):
    method: Literal["pago_movil", "c2p", "vpos"]
    """
    `pago_movil`: the customer sends a Pago Móvil (verify). `c2p`: bank debit with the customer's OTP. `vpos`: card.
    """
    available: bool
    """
    Whether your account can take this method right now.
    """
    reason: Optional[
        Literal[
            "not_enabled", "receiving_account_not_configured", "provider_not_configured"
        ]
    ] = None
    """
    Only when available is false. `not_enabled`: the method is not enabled on your account. `receiving_account_not_configured`: Pago Móvil receiving details are not set up yet. `provider_not_configured`: temporarily unavailable in this mode — contact support.
    """


class PaymentMethodsResponseDto(BaseModel):
    livemode: bool
    """
    false for test keys.
    """
    methods: list[PaymentMethodAvailabilityDto]


class PagoMovilReceivingAccountDto(BaseModel):
    provider: Literal["r4", "bnc", "sofitasa"] = Field(..., examples=["r4"])
    """
    Provider Pago Móvil verify uses for this tenant (same routing as POST /v1/payments/pago-movil/verify).
    """
    bankCode: str = Field(..., examples=["0169"])
    """
    Four-digit SIMF code of the receiving bank.
    """
    bankName: str = Field(..., examples=["Mi Banco"])
    phone: Optional[str] = Field(..., examples=["04125555555"])
    """
    Phone the customer sends the Pago Móvil to (11 digits). Null when not configured.
    """
    identification: Optional[str] = Field(..., examples=["13536734"])
    """
    Cédula/RIF of the receiving account, as configured. Null when not configured.
    """
    configured: bool
    """
    True when every receiving detail is set. Do not offer Pago Móvil to customers while false.
    """
    missing: list[Literal["phone", "identification"]] = Field(..., examples=[[]])
    """
    Receiving details that are not configured yet.
    """
    livemode: bool
    """
    False for test-mode API keys.
    """


class PagoMovilVerifyDto(BaseModel):
    usdAmount: float = Field(..., examples=[25], ge=0.01, le=100000.0)
    reference: str = Field(..., examples=["12345678"], max_length=32, min_length=4)
    dateMovement: Optional[date] = Field(None, examples=["2026-07-20"])
    externalRef: Optional[str] = Field(None, examples=["order-1042"], max_length=64)
    """
    Correlation value; not an idempotency key.
    """
    debtorBankCode: Optional[str] = Field(None, examples=["0102"])
    """
    Payer bank SIMF code. Required for some receiving banks — send it whenever you have it.
    """
    txType: Optional[Literal["pago_movil", "transferencia", "debito_inmediato"]] = (
        Field(None, examples=["transferencia"])
    )
    """
    Instrument type, required by some receiving banks. Defaults to transferencia.
    """
    debtorCellPhone: Optional[str] = Field(None, examples=["04149333844"])
    """
    Payer Pago Móvil phone (11-digit local, e.g. 04149333844). Required by some receiving banks when txType is pago_movil — send it whenever you have it.
    """
    onwardPayout: Optional[OnwardPayoutDto] = None
    """
    Convert this payment's net VES to USDT once it completes and send it to this wallet. Needs USDT and conversions enabled; not allowed with merchantId. See the "Pay in bolívars, receive USDT" guide.
    """


class PayoutMethodResponseDto(BaseModel):
    payoutMethodId: str
    bankCode: str = Field(..., examples=["0134"])
    destination: str
    """
    Masked phone destination, e.g. …5555
    """
    status: Literal["pending_verification", "verifying", "verified", "rejected"]
    isDefault: bool
    failureCode: Optional[str] = None
    lockedUntil: Optional[str] = None
    verifiedAt: Optional[str] = None
    createdAt: Optional[str] = None


class MerchantResponseDto(BaseModel):
    merchantId: str
    accountId: str = Field(..., examples=["acct_3fd84b2d9ad14f74a2d90f2f56984db5"])
    externalRef: str
    name: Optional[str] = Field(None, examples=["Maria Perez"], max_length=20)
    status: Literal["pending_verification", "verifying", "verified", "rejected"]
    """
    Mirrored from the default payout method
    """
    isActive: bool
    """
    When false, merchant cannot receive new payouts
    """
    autoPayoutEnabled: Optional[bool] = None
    """
    When true, available balance is auto-paid to the default verified method.
    """
    applicationFeePercent: Optional[float] = Field(None, examples=[12.5])
    """
    Merchant-specific marketplace commission percent. null = the tenant's default commission applies.
    """
    bankCode: Optional[str] = None
    """
    Default method bank code (compat)
    """
    destination: Optional[str] = None
    """
    Masked default method phone (compat)
    """
    payoutMethods: Optional[list[PayoutMethodResponseDto]] = None
    message: Optional[str] = Field(
        None,
        examples=[
            "No payout method exists. Add one with POST /v1/merchants/:id/payout-methods before verifying or paying out."
        ],
    )
    """
    Present when the merchant has no payout methods yet (e.g. created without bankCode/phone)
    """
    failureCode: Optional[str] = None
    lockedUntil: Optional[str] = None
    """
    ISO timestamp; when set and in the future, verification is locked
    """
    deactivatedAt: Optional[str] = None
    """
    ISO timestamp when the merchant was deactivated
    """
    createdAt: Optional[str] = None
    verifiedAt: Optional[str] = None
    ownerType: Optional[Literal["tenant", "wallet"]] = None
    """
    How the merchant was created.
    """
    merchantType: Optional[Literal["INDIVIDUAL", "COMPANY"]] = None
    displayName: Optional[str] = None
    walletUserId: Optional[str] = None
    """
    VEX Wallet user id (`ownerType = "wallet"`).
    """
    rifNumber: Optional[str] = None
    accountStatus: Optional[Literal["active", "pending", "restricted", "rejected"]] = (
        None
    )
    """
    VEX Pay-owned compliance lifecycle, independent of payout `status`.
    """
    kybStatus: Optional[
        Literal["not_required", "required", "pending", "verified", "rejected"]
    ] = None
    restrictionReason: Optional[str] = None
    activatedAt: Optional[AwareDatetime] = None
    capabilities: Optional[dict[str, Any]] = None
    """
    Effective payment capabilities (stored grant AND accountStatus = active). Null for merchants with no capabilities row.
    """


class MerchantListResponseDto(BaseModel):
    items: list[MerchantResponseDto]
    nextCursor: Optional[str] = None
    """
    Pass as cursor on the next request when more pages exist
    """


class MerchantAuditEventDto(BaseModel):
    id: str
    event: str = Field(..., examples=["MERCHANT_UPDATED"])
    """
    SCREAMING_SNAKE lifecycle event, e.g. MERCHANT_CREATED | MERCHANT_ACTIVATED | RIF_SUBMITTED | CAPABILITY_ENABLED | MERCHANT_UPDATED | MERCHANT_RESTRICTED.
    """
    actor: str = Field(..., examples=["wallet:usr_123"])
    """
    "wallet:<sub>" | "system" | "platform:<sub>".
    """
    data: Optional[dict[str, Any]] = None
    """
    Event-specific detail, e.g. { fields: ["instagram"] }.
    """
    createdAt: AwareDatetime


class MerchantAuditEventListDto(BaseModel):
    items: list[MerchantAuditEventDto]


class DeleteMerchantResponseDto(BaseModel):
    deleted: bool = Field(..., examples=[True])
    merchantId: str
    externalRef: str = Field(..., examples=["usr_7f3a"])


class PayoutMethodListResponseDto(BaseModel):
    items: list[PayoutMethodResponseDto]


class VerifyStartResponseDto(BaseModel):
    status: str = Field(..., examples=["verifying"])
    expiresAt: str = Field(..., examples=["2026-07-22T02:30:00Z"])
    payoutMethodId: Optional[str] = None


class VerifyConfirmResponseDto(BaseModel):
    status: str = Field(..., examples=["verified"])
    payoutMethodId: str


class MerchantCopBalanceDto(BaseModel):
    pendingCop: str = Field(..., examples=["16002"])
    """
    COP sales still in the seller hold.
    """
    availableCop: str = Field(..., examples=["30000"])
    """
    COP the seller can pay out.
    """
    payoutPendingCop: str = Field(..., examples=["0"])
    """
    COP payouts requested and not yet paid.
    """
    paidOutCop: str = Field(..., examples=["0"])
    """
    COP paid out to the seller so far.
    """
    sweepRate: Optional[str] = Field(None, examples=["3939.0000"])
    """
    VEX Wallet sellers: COP per US$1 a wallet sweep would use now (display only). Omitted when no fresh rate.
    """


class MerchantBalanceDto(BaseModel):
    merchantId: str
    accountId: str = Field(..., examples=["acct_3fd84b2d9ad14f74a2d90f2f56984db5"])
    tenantId: str
    pendingVes: str = Field(..., examples=["100.00"])
    availableVes: str = Field(..., examples=["250.00"])
    paidOutVes: str = Field(..., examples=["50.00"])
    ledgerNetVes: str = Field(..., examples=["350.00"])
    cop: Optional[MerchantCopBalanceDto] = None
    """
    COP balances from COP sales on seller links. Present only once the seller has COP activity.
    """


class CreateMerchantDto(BaseModel):
    externalRef: str = Field(..., examples=["usr_7f3a…"], max_length=64)
    name: str = Field(..., examples=["Maria Perez"], max_length=20)
    identification: str = Field(..., examples=["V12345678"])
    """
    V/E+8 or J/G+9
    """
    contactEmail: str = Field(..., examples=["maria@mail.com"])
    contactPhone: str = Field(..., examples=["04141234567"])
    bankCode: Optional[str] = Field(None, examples=["0134"])
    """
    Optional 4-digit SIMF bank code for the first Pago Móvil payout method. Provide together with phone, or omit both to create a merchant shell with no payout method.
    """
    phone: Optional[str] = Field(None, examples=["04145555555"])
    """
    Optional 11-digit local Pago Móvil phone for the first payout method. Provide together with bankCode, or omit both.
    """


class CreatePayoutMethodDto(BaseModel):
    bankCode: str = Field(..., examples=["0134"])
    """
    4-digit SIMF bank code
    """
    phone: str = Field(..., examples=["04145555555"])
    """
    11-digit local Pago Móvil phone
    """


class ConfirmMerchantVerifyDto(BaseModel):
    amount1: str = Field(..., examples=["0.37"])
    """
    Exact two-decimal VES amount
    """
    amount2: str = Field(..., examples=["0.82"])
    """
    Exact two-decimal VES amount
    """


class CreateMerchantTransferDto(BaseModel):
    amountVes: Optional[str] = Field(None, examples=["1523.40"])
    """
    Exact two-decimal VES amount to move from platform float → seller pending. Send this or `amountUsd`, not both.
    """
    amountUsd: Optional[str] = Field(None, examples=["100.00"])
    """
    Exact two-decimal USD amount, converted to VES at the official BCV rate at the time of the request (regardless of your account’s Bolívar rate setting). The rate is saved with the transfer and a replay returns it. Send this or `amountVes`, not both.
    """
    transferKey: str = Field(..., examples=["xfer_bid_1042"], max_length=64)
    """
    Idempotency key for this transfer under the merchant.
    """
    paymentId: Optional[str] = None
    """
    Optional funding payment correlation (does not enforce remaining-net).
    """


class MerchantTransferSnapshotDto(BaseModel):
    transferKey: str = Field(..., examples=["q1-nov-2026-u123"])
    amountVes: str = Field(..., examples=["21540.00"])
    """
    VES credited to the merchant.
    """
    amountUsd: Optional[str] = Field(None, examples=["100.00"])
    """
    USD transfers only: the USD amount requested.
    """
    rate: Optional[str] = Field(None, examples=["215.4000"])
    """
    USD transfers only: the BCV rate used.
    """
    rateSource: Optional[str] = Field(None, examples=["bcv"])
    """
    USD transfers only: always `bcv`.
    """
    rateAsOf: Optional[AwareDatetime] = None
    """
    USD transfers only: when the rate was read.
    """


class MerchantTransferResponseDto(BaseModel):
    merchantId: str
    accountId: str = Field(..., examples=["acct_3fd84b2d9ad14f74a2d90f2f56984db5"])
    tenantId: str
    pendingVes: str = Field(..., examples=["100.00"])
    availableVes: str = Field(..., examples=["250.00"])
    paidOutVes: str = Field(..., examples=["50.00"])
    ledgerNetVes: str = Field(..., examples=["350.00"])
    cop: Optional[MerchantCopBalanceDto] = None
    """
    COP balances from COP sales on seller links. Present only once the seller has COP activity.
    """
    transfer: MerchantTransferSnapshotDto
    """
    What this transfer credited (the original values on a replay).
    """


class MerchantMovementDto(BaseModel):
    id: str
    type: Literal[
        "credit",
        "release",
        "reversal",
        "payout",
        "payout_reversal",
        "payout_fee",
        "payout_fee_reversal",
        "adjustment",
    ] = Field(..., examples=["credit"])
    amountVes: str = Field(..., examples=["21540.00"])
    """
    Signed change of the total balance (pending + available). A `release` row is 0.00.
    """
    releasedVes: Optional[str] = Field(None, examples=["21540.00"])
    """
    `release` rows only: VES moved from pending to available (negative = put back on hold).
    """
    description: str = Field(..., examples=["Credit"])
    transferKey: Optional[str] = Field(None, examples=["q1-nov-u1"])
    """
    `credit` rows: the transferKey you sent.
    """
    paymentId: Optional[str] = None
    payoutId: Optional[str] = None
    availableAt: Optional[AwareDatetime] = None
    """
    `credit` rows: when the credit becomes withdrawable.
    """
    amountUsd: Optional[str] = Field(None, examples=["100.00"])
    """
    Credits sent with `amountUsd`: the USD amount.
    """
    rate: Optional[str] = Field(None, examples=["215.4000"])
    """
    Credits sent with `amountUsd`: the rate used.
    """
    rateSource: Optional[str] = Field(None, examples=["bcv"])
    createdAt: AwareDatetime


class MerchantMovementListDto(BaseModel):
    items: list[MerchantMovementDto]
    nextCursor: Optional[str] = Field(...)
    """
    Pass as `cursor` for the next (older) page; null on the last page.
    """


class MerchantStatementDto(BaseModel):
    merchantId: str
    month: str = Field(..., examples=["2026-11"])
    from_: AwareDatetime = Field(
        ..., alias="from", examples=["2026-11-01T04:00:00.000Z"]
    )
    """
    Month start, America/Caracas.
    """
    to: AwareDatetime = Field(..., examples=["2026-12-01T04:00:00.000Z"])
    """
    Month end (exclusive), America/Caracas.
    """
    openingVes: str = Field(..., examples=["0.00"])
    closingVes: str = Field(..., examples=["21800.00"])
    """
    openingVes + Σ movements[].amountVes.
    """
    movements: list[MerchantMovementDto]
    """
    Oldest first.
    """


class UpdateMerchantDto(BaseModel):
    isActive: Optional[bool] = None
    """
    Soft off-switch for payouts. false = deactivated (history kept).
    """
    autoPayoutEnabled: Optional[bool] = None
    """
    When true, a cron job automatically pays available seller balance to the default verified Pago Móvil method.
    """
    applicationFeePercent: Optional[float] = Field(
        None, examples=[12.5], ge=0.0, le=100.0
    )
    """
    Negotiated marketplace commission (percent of vesAmount) retained from payments tagged with this merchant when the request sends no applicationFeeVes / applicationFeePercent. null clears the override so the tenant's default commission applies.
    """


class CreateCheckoutSessionDto(BaseModel):
    amountUsd: float = Field(..., examples=[25], ge=0.01, le=100000.0)
    """
    USD amount, up to 2 decimals.
    """
    description: Optional[str] = Field(None, examples=["Pedido #1042"], max_length=200)
    """
    Buyer-facing label on the checkout.
    """
    reference: Optional[str] = Field(None, examples=["order-1042"], max_length=64)
    """
    Your reference, echoed on reads and webhooks.
    """
    expiresInMinutes: float = Field(60, examples=[60], ge=5.0, le=1440.0)
    successUrl: Optional[str] = Field(None, examples=["https://shop.example/gracias"])
    """
    Where the hosted page sends the buyer after paying. https only (http://localhost allowed for test tenants).
    """
    cancelUrl: Optional[str] = Field(None, examples=["https://shop.example/carrito"])
    """
    Where a buyer who backs out is sent.
    """
    allowedOrigins: Optional[list[str]] = Field(
        None, examples=[["https://shop.example"]]
    )
    """
    Origins allowed to embed this checkout with @vexpay/js. https only; http://localhost:* allowed for test tenants. Omit to allow the hosted URL only.
    """
    methods: Optional[
        list[Literal["c2p", "pago_movil", "vpos", "usdt", "usdc", "cop"]]
    ] = None
    """
    Payment methods offered. Defaults to every method your account can accept. `c2p` is the bank pull shown as Débito Inmediato; `pago_movil` is a Pago Móvil the buyer sends from their bank app (needs Pago Móvil enabled on your account). `cop` (Colombian pesos: Bre-B, Nequi, Daviplata) needs the COP method on your account.
    """
    metadata: Optional[dict[str, str]] = Field(None, examples=[{"orderId": "1042"}])
    """
    Up to 20 string key/value pairs (keys ≤ 40 chars, values ≤ 500 chars).
    """
    merchantId: Optional[str] = Field(
        None, examples=["3fd84b2d-9ad1-4f74-a2d9-0f2f56984db5"]
    )
    """
    Split the payment with one of your merchants (UUID or `mrc_` id). The merchant's share is credited to its VES balance when the payment completes. Only bolívar methods (`c2p`, `pago_movil`, `vpos`) are offered.
    """
    applicationFeePercent: Optional[float] = Field(None, examples=[3], ge=0.0, le=100.0)
    """
    Commission percent you keep when `merchantId` is set. Omit to use the merchant's commission, then your default commission.
    """


class CheckoutSessionResponseDto(BaseModel):
    id: str = Field(..., examples=["cs_4f0c6f1e2b7d4c1a9e3f5a6b7c8d9e0f"])
    object: Literal["checkout.session"]
    status: Literal["open", "processing", "paid", "failed", "expired", "canceled"]
    """
    `processing` while a bank charge is in flight; `failed` when the latest attempt failed (the buyer may retry until expiresAt).
    """
    clientSecret: Optional[str] = Field(None, examples=["cs-9f2a4b7c1d3e_secret_k8Jc…"])
    """
    Returned only by create. Pass it to @vexpay/js in the browser; never store or log it.
    """
    url: str = Field(..., examples=["https://pay.vexwallet.co/pay/cs-9f2a4b7c1d3e"])
    amountUsd: str = Field(..., examples=["25.00"])
    description: Optional[str] = None
    reference: Optional[str] = None
    metadata: dict[str, str]
    allowedOrigins: list[str]
    methods: list[Literal["c2p", "pago_movil", "vpos", "usdt", "usdc", "cop"]]
    successUrl: Optional[str] = None
    cancelUrl: Optional[str] = None
    paymentId: Optional[str] = None
    """
    Latest payment for this session, once one exists.
    """
    expiresAt: AwareDatetime
    createdAt: AwareDatetime
    merchantId: Optional[str] = None
    """
    Merchant the payment is split with.
    """
    applicationFeePercent: Optional[str] = Field(None, examples=["3"])
    """
    Commission percent set on the session; null = merchant or tenant default at payment time.
    """
    livemode: bool
    """
    false for test-mode tenants.
    """


class PaymentLinkResponseDto(BaseModel):
    id: str
    productId: str
    slug: str = Field(..., examples=["camiseta-vexpay"])
    hostedCheckoutPath: str = Field(..., examples=["/pay/camiseta-vexpay"])
    """
    Path of the hosted checkout page.
    """
    status: Literal["active", "disabled"]
    allowQuantity: bool
    maxQuantity: Optional[float] = None
    redirectUrl: Optional[str] = None
    createdAt: AwareDatetime


class ProductResponseDto(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    priceUsd: str = Field(..., examples=["20.00"])
    active: bool
    createdAt: AwareDatetime
    updatedAt: AwareDatetime
    links: Optional[list[PaymentLinkResponseDto]] = None


class ProductListResponseDto(BaseModel):
    items: list[ProductResponseDto]
    nextCursor: Optional[str] = None
    """
    Pass as ?cursor= for the next page.
    """


class PaymentLinkListResponseDto(BaseModel):
    items: list[PaymentLinkResponseDto]


class CreateProductDto(BaseModel):
    name: str = Field(..., examples=["Camiseta VEXPay"], max_length=120)
    description: Optional[str] = Field(None, max_length=2000)
    imageUrl: Optional[str] = Field(None, examples=["https://cdn.example/shirt.png"])
    priceUsd: str = Field(..., examples=["20.00"])
    """
    Positive USD price, up to 2 decimals.
    """
    active: bool = True


class UpdateProductDto(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    description: Optional[str] = Field(None, max_length=2000)
    imageUrl: Optional[str] = None
    priceUsd: Optional[str] = Field(None, examples=["25.00"])
    active: Optional[bool] = None


class CreatePaymentLinkDto(BaseModel):
    slug: Optional[str] = Field(None, examples=["camiseta-vexpay"])
    """
    URL slug for the hosted checkout. Lowercase letters, digits, hyphens. Auto-generated from the product name when omitted.
    """
    allowQuantity: bool = False
    """
    Let the buyer choose a quantity.
    """
    maxQuantity: Optional[float] = Field(None, ge=1.0, le=999.0)
    redirectUrl: Optional[str] = None
    """
    Where to send the buyer after a successful payment.
    """


class UpdatePaymentLinkDto(BaseModel):
    status: Optional[Literal["active", "disabled"]] = None
    allowQuantity: Optional[bool] = None
    maxQuantity: Optional[float] = Field(None, ge=1.0, le=999.0)
    redirectUrl: Optional[str] = None


class CreateTopupDto(BaseModel):
    amountVes: str = Field(..., examples=["100000.00"])
    """
    Bs to load, two decimals, above 0.
    """
    payerPhone: str = Field(..., examples=["04121234567"])
    """
    Phone the Pago Móvil is sent from (Venezuelan mobile, 04XXXXXXXXX).
    """
    payerCedula: str = Field(..., examples=["V12345678"])
    """
    Cédula or RIF of the payer.
    """
    sourceNote: str = Field(..., examples=["Ingresos de publicidad, quincena 2"])
    """
    Where the money comes from (10–500 characters). Visible to VEX Pay ops.
    """


class TopupReceiverDto(BaseModel):
    bankCode: str = Field(..., examples=["0169"])
    """
    Bank code to pick in your bank app. The bank name is not shown.
    """
    phone: str = Field(..., examples=["04140000000"])
    identification: str = Field(..., examples=["J-000000000"])


class TopupDto(BaseModel):
    id: str
    status: Literal["pending", "completed", "expired", "failed", "reversed"]
    amountVes: str = Field(..., examples=["100000.00"])
    amountUsd: str = Field(..., examples=["500.00"])
    """
    USD at the BCV rate snapshotted at creation.
    """
    bcvRate: str = Field(..., examples=["200.0000"])
    feePercent: str = Field(..., examples=["3.5000"])
    feeFixedUsd: str = Field(..., examples=["0.25"])
    feeVes: Optional[str] = Field(None, examples=["3550.00"])
    """
    Charged when the top-up completes.
    """
    creditedVes: Optional[str] = Field(None, examples=["96450.00"])
    """
    Credited to your balance (amount − fee).
    """
    sourceNote: str
    payerPhone: str
    bankReference: Optional[str] = None
    expiresAt: str
    completedAt: Optional[str] = None
    availableAt: Optional[str] = None
    """
    When the credit becomes available on its own (null = available).
    """
    heldVes: str = Field(..., examples=["96450.00"])
    """
    Part of this top-up still held.
    """
    instantFeePercent: str = Field(..., examples=["1.5000"])
    """
    Instant availability fee percent.
    """
    instantFeeVes: str = Field(..., examples=["1446.75"])
    """
    Fee to release heldVes now.
    """
    instantReleasedAt: Optional[str] = None
    """
    When the held part was released early with the instant fee.
    """
    receiver: Optional[TopupReceiverDto] = None
    """
    Where to send the Pago Móvil (pending only).
    """
    test: bool
    createdAt: str


class TopupListDto(BaseModel):
    data: list[TopupDto]
    monthlyCapUsd: Optional[str] = Field(..., examples=["3000.00"])
    monthUsedUsd: str = Field(..., examples=["500.00"])
    monthRemainingUsd: str = Field(..., examples=["2500.00"])


class NotificationTestResponseDto(BaseModel):
    sent: bool = Field(..., examples=[True])
    event: str = Field(..., examples=["notification.test"])
    tenantId: str


class CreateCustomerDto(BaseModel):
    name: Optional[str] = Field(None, examples=["Ana Pérez"], max_length=120)
    email: Optional[str] = Field(None, examples=["ana@example.com"], max_length=254)
    phone: Optional[str] = Field(None, examples=["04141234567"])
    """
    Venezuelan mobile; stored as 11 digits starting with 04.
    """
    idNumber: Optional[str] = Field(None, examples=["V-12.345.678"])
    """
    Cédula or RIF; stored canonical, e.g. V12345678.
    """
    bankCode: Optional[str] = Field(None, examples=["0102"])
    """
    4-digit bank code from GET /v1/banks.
    """
    metadata: Optional[dict[str, str]] = None
    """
    ≤ 20 string key/value pairs.
    """
    testClock: Optional[str] = None
    """
    Test clock id (test mode only). Not available yet.
    """


class CustomerResponseDto(BaseModel):
    id: str = Field(..., examples=["cus_3fd84b2d9ad14f74a2d90f2f56984db5"])
    object: str = Field(..., examples=["customer"])
    name: Optional[str] = Field(...)
    email: Optional[str] = Field(...)
    emailStatus: Literal["none", "deliverable", "undeliverable"]
    phone: Optional[str] = Field(...)
    idNumber: Optional[str] = Field(...)
    bankCode: Optional[str] = Field(...)
    metadata: dict[str, str]
    testClock: Optional[str] = Field(...)
    createdAt: str
    livemode: bool


class CustomerListResponseDto(BaseModel):
    items: list[CustomerResponseDto]
    nextCursor: Optional[str] = Field(...)


class UpdateCustomerDto(BaseModel):
    name: Optional[str] = Field(None, examples=["Ana Pérez"], max_length=120)
    email: Optional[str] = Field(None, examples=["ana@example.com"], max_length=254)
    phone: Optional[str] = Field(None, examples=["04141234567"])
    """
    Venezuelan mobile; stored as 11 digits starting with 04.
    """
    idNumber: Optional[str] = Field(None, examples=["V-12.345.678"])
    """
    Cédula or RIF; stored canonical, e.g. V12345678.
    """
    bankCode: Optional[str] = Field(None, examples=["0102"])
    """
    4-digit bank code from GET /v1/banks.
    """
    metadata: Optional[dict[str, str]] = None
    """
    ≤ 20 string key/value pairs.
    """
    testClock: Optional[str] = None
    """
    Test clock id (test mode only). Not available yet.
    """


class DeletedObjectResponseDto(BaseModel):
    id: str
    deleted: bool = Field(..., examples=[True])


class RecurringDto(BaseModel):
    interval: Literal["day", "week", "month", "year"] = Field(..., examples=["month"])
    intervalCount: float = Field(1, examples=[1])
    """
    The whole interval is at most one year.
    """


class CreatePriceDto(BaseModel):
    product: str
    """
    Product id.
    """
    unitAmountUsd: float = Field(..., examples=[10])
    """
    USD amount, up to 2 decimals, at least the minimum charge.
    """
    recurring: RecurringDto
    nickname: Optional[str] = Field(None, max_length=80)
    metadata: Optional[dict[str, str]] = None


class PriceRecurringResponseDto(BaseModel):
    interval: Literal["day", "week", "month", "year"]
    intervalCount: float


class PriceResponseDto(BaseModel):
    id: str = Field(..., examples=["price_3fd84b2d9ad14f74a2d90f2f56984db5"])
    object: str = Field(..., examples=["price"])
    product: str
    unitAmountUsd: str = Field(..., examples=["10.00"])
    currency: str = Field(..., examples=["USD"])
    recurring: PriceRecurringResponseDto
    nickname: Optional[str] = Field(...)
    active: bool
    metadata: dict[str, str]
    createdAt: str
    livemode: bool


class PriceListResponseDto(BaseModel):
    items: list[PriceResponseDto]
    nextCursor: Optional[str] = Field(...)


class UpdatePriceDto(BaseModel):
    active: Optional[bool] = None
    nickname: Optional[str] = Field(None, max_length=80)
    metadata: Optional[dict[str, str]] = None


class CreateSubscriptionDto(BaseModel):
    customer: str
    """
    Customer id (cus_…).
    """
    price: str
    """
    Active recurring price id (price_…).
    """
    collectionMethod: Literal["send_invoice", "charge_automatically"] = "send_invoice"
    """
    `charge_automatically` charges the customer's domiciliación on each collection attempt; the tenant must be allowed domiciliación.
    """
    collectionAttempts: Optional[float] = Field(None, ge=1.0, le=15.0)
    """
    Daily collection attempts on each invoice before the subscription is canceled. Omit or null for the tenant's default (3 unless changed).
    """
    paymentMethod: Optional[str] = None
    """
    Domiciliación payment method (pm_…, charge_automatically only). Default: the customer's most recent method that is not inactive.
    """
    trialPeriodDays: Optional[float] = Field(None, ge=1.0, le=730.0)
    trialEnd: Optional[str] = None
    """
    ISO time in the future when the trial ends.
    """
    cancelAtPeriodEnd: bool = False
    methods: Optional[
        list[Literal["c2p", "pago_movil", "vpos", "usdt", "usdc", "cop"]]
    ] = None
    """
    Hosted checkout methods offered on its invoices.
    """
    metadata: Optional[dict[str, str]] = None


class SubscriptionResponseDto(BaseModel):
    id: str = Field(..., examples=["sub_3fd84b2d9ad14f74a2d90f2f56984db5"])
    object: str = Field(..., examples=["subscription"])
    customer: str
    price: PriceResponseDto
    status: Literal["trialing", "active", "past_due", "canceled"]
    collectionMethod: Literal["send_invoice", "charge_automatically"]
    collectionAttempts: Optional[float] = Field(...)
    """
    Null = the tenant's default.
    """
    paymentMethod: Optional[str] = Field(...)
    currentPeriodStart: str
    currentPeriodEnd: str
    trialStart: Optional[str] = Field(...)
    trialEnd: Optional[str] = Field(...)
    cancelAtPeriodEnd: bool
    canceledAt: Optional[str] = Field(...)
    cancellationReason: Optional[Literal["requested", "payment_failed"]] = Field(...)
    latestInvoice: Optional[str] = Field(...)
    methods: list[Literal["c2p", "pago_movil", "vpos", "usdt", "usdc", "cop"]]
    metadata: dict[str, str]
    createdAt: str
    livemode: bool


class SubscriptionListResponseDto(BaseModel):
    items: list[SubscriptionResponseDto]
    nextCursor: Optional[str] = Field(...)


class UpdateSubscriptionDto(BaseModel):
    cancelAtPeriodEnd: Optional[bool] = None
    collectionMethod: Optional[Literal["send_invoice", "charge_automatically"]] = None
    paymentMethod: Optional[str] = None
    collectionAttempts: Optional[float] = Field(None, ge=1.0, le=15.0)
    """
    null = the tenant's default.
    """
    methods: Optional[
        list[Literal["c2p", "pago_movil", "vpos", "usdt", "usdc", "cop"]]
    ] = None
    metadata: Optional[dict[str, str]] = None


class InvoiceBillingFeeResponseDto(BaseModel):
    amount: str = Field(..., examples=["43.90"])
    currency: Literal["VES", "USDT", "USDC", "COP"]
    percent: str = Field(..., examples=["0.5"])


class InvoiceResponseDto(BaseModel):
    id: str = Field(..., examples=["in_3fd84b2d9ad14f74a2d90f2f56984db5"])
    object: str = Field(..., examples=["invoice"])
    number: str = Field(..., examples=["K7Q2M9XA-0001"])
    status: Literal["open", "paid", "void", "uncollectible"]
    customer: str
    subscription: str
    collectionMethod: Literal["send_invoice", "charge_automatically"]
    amountDueUsd: str = Field(..., examples=["10.00"])
    amountPaidUsd: str = Field(..., examples=["0.00"])
    currency: str = Field(..., examples=["USD"])
    periodStart: str
    periodEnd: str
    dueDate: str
    """
    Invoices are due when issued.
    """
    attemptsTotal: float
    """
    Daily collection attempts for this invoice.
    """
    attemptCount: float
    nextPaymentAttempt: Optional[str] = Field(...)
    paidAt: Optional[str] = Field(...)
    paidOutOfBand: bool
    paymentId: Optional[str] = Field(...)
    billingFee: Optional[InvoiceBillingFeeResponseDto] = Field(...)
    hostedInvoiceUrl: Optional[str] = Field(...)
    createdAt: str
    livemode: bool


class InvoiceListResponseDto(BaseModel):
    items: list[InvoiceResponseDto]
    nextCursor: Optional[str] = Field(...)


class PayInvoiceDto(BaseModel):
    paidOutOfBand: bool = Field(..., examples=[True])
    """
    Mark the invoice paid outside VEXPay (cash, transfer). No balance change.
    """


class CreateSetupSessionDto(BaseModel):
    customer: str
    """
    Customer id (cus_…).
    """
    successUrl: Optional[str] = Field(None, max_length=2048)
    """
    Where the setup page sends the customer when done (https).
    """


class SetupSessionResponseDto(BaseModel):
    id: str = Field(..., examples=["seti_3fd84b2d9ad14f74a2d90f2f56984db5"])
    object: str = Field(..., examples=["setup_session"])
    url: Optional[str] = Field(...)
    """
    Hosted authorization page. Only returned on create.
    """
    customer: str
    status: Literal["open", "complete", "expired"]
    paymentMethod: Optional[str] = Field(...)
    successUrl: Optional[str] = Field(...)
    expiresAt: str
    createdAt: str
    livemode: bool


class PaymentMethodResponseDto(BaseModel):
    id: str = Field(..., examples=["pm_3fd84b2d9ad14f74a2d90f2f56984db5"])
    object: str = Field(..., examples=["payment_method"])
    type: str = Field(..., examples=["domiciliacion"])
    customer: str
    status: Literal["pending", "active", "inactive"]
    """
    pending until a charge succeeds; inactive when the bank reports the affiliation inactive.
    """
    phoneLast4: str = Field(..., examples=["4567"])
    bankCode: str = Field(..., examples=["0102"])
    createdAt: str
    activatedAt: Optional[str] = Field(...)
    deactivatedAt: Optional[str] = Field(...)
    detachedAt: Optional[str] = Field(...)
    """
    Set once detached; a detached method is never charged.
    """
    livemode: bool


class PaymentMethodListResponseDto(BaseModel):
    items: list[PaymentMethodResponseDto]
    nextCursor: Optional[str] = Field(...)
