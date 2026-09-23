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
    Machine-readable error code (e.g. `external_ref_conflict`, `insufficient_balance`, `idempotency_key_reused`) or, for Nest default errors, a short label such as `Bad Request`. Domain errors may include extra route-specific fields.
    """


class PlatformBalanceDto(BaseModel):
    tenantId: str
    platformId: str = Field(..., examples=["plt_3fd84b2d9ad14f74a2d90f2f56984db5"])
    collectedVes: str = Field(..., examples=["10000.00"])
    feesVes: str = Field(..., examples=["250.00"])
    paidOutVes: str = Field(..., examples=["1000.00"])
    reserveVes: str = Field(..., examples=["100.00"])
    ledgerNetVes: str = Field(..., examples=["8650.00"])
    availableVes: str = Field(..., examples=["8650.00"])
    """
    Tenant spendable float after reserve (seller obligations already deducted via SELLER_TRANSFER).
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
            "tenant.status_changed",
            "tenant.api_key.created",
            "tenant.api_key.rotated",
            "tenant.api_key.revoked",
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
            "tenant.status_changed",
            "tenant.api_key.created",
            "tenant.api_key.rotated",
            "tenant.api_key.revoked",
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
                "tenant.status_changed",
                "tenant.api_key.created",
                "tenant.api_key.rotated",
                "tenant.api_key.revoked",
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
    status: Literal["completed", "pending", "failed"]
    """
    `pending` means the credit is still reconciling (AC00); subscribe to payout webhooks or poll GET /v1/payouts/:id.
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
    Platform fee in VES retained on instant tenant credits.
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
    status: Literal["completed", "pending", "failed"]
    """
    `pending` means the credit is still reconciling (AC00); subscribe to payout webhooks or poll GET /v1/payouts/:id.
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
    Platform fee in VES retained on instant tenant credits.
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
    Tenant correlation value for recovery lookup (GET /v1/payments/by-ref/:externalRef). Not an idempotency key.
    """
    merchantId: Optional[str] = None
    applicationFeeVes: Optional[str] = Field(None, examples=["50.00"])
    """
    Marketplace application fee in VES retained by the platform.
    """
    applicationFeePercent: Optional[float] = Field(
        None, examples=[10], ge=0.0, le=100.0
    )


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
    Authoritative VEX FX BCV rate used for payment settlement
    """
    vesAmount: float = Field(..., examples=[912.5])
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
    Per-source BCV rates or error objects (e.g. `{ error: "BANK_NOT_CONFIGURED" }`). Keys typically include `vexFx` and `bank`. `sources.bank` prefers R4 MBbcv, then falls back to BNC Services/BCVRates (`provider: "r4" | "bnc"`).
    """


class C2pRequestDto(BaseModel):
    usdAmount: float = Field(..., examples=[25], ge=0.01, le=100000.0)
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
    Correlation value; not an idempotency key. When present, any other PENDING C2P intent for this tenant + externalRef is canceled (superseded) before the new intent is created.
    """
    merchantId: Optional[str] = None
    applicationFeeVes: Optional[str] = Field(None, examples=["50.00"])
    """
    Marketplace application fee in VES retained by the platform.
    """
    applicationFeePercent: Optional[float] = Field(
        None, examples=[10], ge=0.0, le=100.0
    )


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
    intentId: str
    """
    Use this value as intentId when executing the C2P charge.
    """
    otpRequested: bool
    """
    true when the provider instructed the payer bank to SMS an OTP to the customer (R4 GenerarOtp). false when the customer must generate the token in their bank app.
    """


class C2pPaymentDto(BaseModel):
    intentId: Optional[str] = None
    """
    Pending intent returned by POST /v1/payments/c2p/request.
    """
    usdAmount: float = Field(..., examples=[25], ge=0.01, le=100000.0)
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
    Correlation value; not an idempotency key.
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
    Optional percent of vesAmount used when applicationFeeVes is omitted.
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


class VposPaymentDto(BaseModel):
    usdAmount: Optional[float] = Field(None, examples=[25], ge=0.01, le=100000.0)
    """
    USD amount. Required unless vesAmount is set. When only usdAmount is set, VES is derived at the live BCV rate.
    """
    vesAmount: Optional[float] = Field(None, examples=[50], ge=0.01, le=100000000.0)
    """
    VES amount charged at the bank. When set, locks the bolívar charge and derives USD at BCV — use this to avoid USD↔VES 2-decimal round-trip drift (e.g. Bs. 50 → $0.07 → Bs. 52.86).
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
    Correlation value; not an idempotency key.
    """
    merchantId: Optional[str] = None
    applicationFeeVes: Optional[str] = Field(None, examples=["50.00"])
    """
    Marketplace application fee in VES retained by the platform.
    """
    applicationFeePercent: Optional[float] = Field(
        None, examples=[10], ge=0.0, le=100.0
    )


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
    Payer bank SIMF code. Required when the resolved provider is Sofitasa; ignored by R4/BNC.
    """
    txType: Optional[Literal["pago_movil", "transferencia", "debito_inmediato"]] = (
        Field(None, examples=["transferencia"])
    )
    """
    Instrument type for providers that need it (Sofitasa). Defaults to transferencia.
    """
    debtorCellPhone: Optional[str] = Field(None, examples=["04149333844"])
    """
    Payer Pago Móvil phone. Required for Sofitasa when txType is pago_movil (11-digit local, e.g. 04149333844). Ignored by R4/BNC and for other Sofitasa tx types (those send 0).
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


class MerchantBalanceDto(BaseModel):
    merchantId: str
    accountId: str = Field(..., examples=["acct_3fd84b2d9ad14f74a2d90f2f56984db5"])
    tenantId: str
    pendingVes: str = Field(..., examples=["100.00"])
    availableVes: str = Field(..., examples=["250.00"])
    paidOutVes: str = Field(..., examples=["50.00"])
    ledgerNetVes: str = Field(..., examples=["350.00"])


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
    amountVes: str = Field(..., examples=["1523.40"])
    """
    Exact two-decimal VES amount to move from platform float → seller pending.
    """
    transferKey: str = Field(..., examples=["xfer_bid_1042"], max_length=64)
    """
    Idempotency key for this transfer under the merchant.
    """
    paymentId: Optional[str] = None
    """
    Optional funding payment correlation (does not enforce remaining-net).
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
    methods: Optional[list[Literal["c2p", "vpos"]]] = None
    """
    Payment methods offered. Defaults to every method your account can accept.
    """
    metadata: Optional[dict[str, str]] = Field(None, examples=[{"orderId": "1042"}])
    """
    Up to 20 string key/value pairs (keys ≤ 40 chars, values ≤ 500 chars).
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
    methods: list[Literal["c2p", "vpos"]]
    successUrl: Optional[str] = None
    cancelUrl: Optional[str] = None
    paymentId: Optional[str] = None
    """
    Latest payment for this session, once one exists.
    """
    expiresAt: AwareDatetime
    createdAt: AwareDatetime
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


class NotificationTestResponseDto(BaseModel):
    sent: bool = Field(..., examples=[True])
    event: str = Field(..., examples=["notification.test"])
    tenantId: str
