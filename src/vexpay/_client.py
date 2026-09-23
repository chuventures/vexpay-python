from __future__ import annotations

import os
from types import TracebackType
from typing import Optional

import httpx

from . import _async_resources as ar
from . import _resources as r
from ._core import AsyncHttp, SyncHttp, _Config
from ._webhooks import Webhook


class VexPay:
    """Synchronous VEXPay client.

    >>> from vexpay import VexPay
    >>> vexpay = VexPay(api_key=os.environ["VEXPAY_API_KEY"])  # doctest: +SKIP
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_network_retries: Optional[int] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        config = _Config(
            api_key if api_key is not None else os.environ.get("VEXPAY_API_KEY"),
            base_url,
            timeout,
            max_network_retries,
        )
        self._http = SyncHttp(config, http_client)
        self.banks = r.Banks(self._http)
        self.quotes = r.Quotes(self._http)
        self.balance = r.Balance(self._http)
        self.payments = r.Payments(self._http)
        self.checkout = r.Checkout(self._http)
        self.merchants = r.Merchants(self._http)
        self.payouts = r.Payouts(self._http)
        self.products = r.Products(self._http)
        self.payment_links = r.PaymentLinks(self._http)
        self.tenant_payout_account = r.TenantPayoutAccount(self._http)
        self.webhook_endpoints = r.WebhookEndpoints(self._http)
        #: Offline helpers: ``construct_event`` verifies deliveries; no API calls.
        self.webhooks = Webhook()

    def close(self) -> None:
        """Close the underlying HTTP connection pool (unless you passed your own ``http_client``)."""
        self._http.close()

    def __enter__(self) -> VexPay:
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.close()


class AsyncVexPay:
    """Asynchronous VEXPay client (same resources as :class:`VexPay`, awaitable)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_network_retries: Optional[int] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        config = _Config(
            api_key if api_key is not None else os.environ.get("VEXPAY_API_KEY"),
            base_url,
            timeout,
            max_network_retries,
        )
        self._http = AsyncHttp(config, http_client)
        self.banks = ar.AsyncBanks(self._http)
        self.quotes = ar.AsyncQuotes(self._http)
        self.balance = ar.AsyncBalance(self._http)
        self.payments = ar.AsyncPayments(self._http)
        self.checkout = ar.AsyncCheckout(self._http)
        self.merchants = ar.AsyncMerchants(self._http)
        self.payouts = ar.AsyncPayouts(self._http)
        self.products = ar.AsyncProducts(self._http)
        self.payment_links = ar.AsyncPaymentLinks(self._http)
        self.tenant_payout_account = ar.AsyncTenantPayoutAccount(self._http)
        self.webhook_endpoints = ar.AsyncWebhookEndpoints(self._http)
        self.webhooks = Webhook()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncVexPay:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self.aclose()
