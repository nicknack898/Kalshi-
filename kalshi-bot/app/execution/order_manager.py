from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from app.clients.kalshi_rest import KalshiRESTClient
from app.schemas import LimitOrderRequest


@dataclass(slots=True)
class SlippageGuardrails:
    max_slippage_dollars: Decimal = Decimal("0.02")
    min_price_dollars: Decimal = Decimal("0.01")
    max_price_dollars: Decimal = Decimal("0.99")


@dataclass(slots=True)
class OrderRecord:
    client_order_id: str
    order_id: str
    market_ticker: str
    side: str
    limit_price_dollars: Decimal
    count_fp: Decimal
    status: str = "open"
    raw: dict[str, Any] = field(default_factory=dict)


class OrderManager:
    """Limit-order-only execution with idempotent client order IDs and reconciliation support."""

    def __init__(
        self,
        client: KalshiRESTClient,
        *,
        slippage: SlippageGuardrails | None = None,
    ) -> None:
        self.client = client
        self.slippage = slippage or SlippageGuardrails()
        self._records_by_client_id: dict[str, OrderRecord] = {}

    @staticmethod
    def build_client_order_id(strategy_id: str, market_ticker: str, side: str, nonce: str | None = None) -> str:
        nonce = nonce or str(time.time_ns())
        seed = f"{strategy_id}:{market_ticker}:{side}:{nonce}"
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        return digest[:32]

    def _validate_limit_workflow(self, order: LimitOrderRequest, reference_price_dollars: Decimal) -> None:
        if order.limit_price_dollars < self.slippage.min_price_dollars or order.limit_price_dollars > self.slippage.max_price_dollars:
            raise ValueError("Limit price outside configured guardrail bounds")

        slippage = abs(order.limit_price_dollars - reference_price_dollars)
        if slippage > self.slippage.max_slippage_dollars:
            raise ValueError(
                f"Slippage guardrail exceeded: {slippage} > {self.slippage.max_slippage_dollars}"
            )

    async def place_limit_order(
        self,
        payload: dict[str, Any],
        *,
        reference_price_dollars: Decimal,
    ) -> OrderRecord:
        order = LimitOrderRequest.from_mapping(payload)
        self._validate_limit_workflow(order, reference_price_dollars)

        if order.client_order_id in self._records_by_client_id:
            return self._records_by_client_id[order.client_order_id]

        response = await self.client.create_order(
            {
                "market_ticker": order.market_ticker,
                "side": order.side,
                "type": "limit",
                "count": str(order.count_fp),
                "yes_price": str(order.limit_price_dollars),
                "client_order_id": order.client_order_id,
            }
        )
        order_data = response.get("order", response)
        record = OrderRecord(
            client_order_id=order.client_order_id,
            order_id=str(order_data.get("order_id", "")),
            market_ticker=order.market_ticker,
            side=order.side,
            limit_price_dollars=order.limit_price_dollars,
            count_fp=order.count_fp,
            status=str(order_data.get("status", "open")),
            raw=order_data,
        )
        self._records_by_client_id[order.client_order_id] = record
        return record

    async def amend_order(
        self,
        *,
        client_order_id: str,
        new_limit_price_dollars: Decimal,
        new_count_fp: Decimal | None = None,
        reference_price_dollars: Decimal,
    ) -> OrderRecord:
        record = self._records_by_client_id[client_order_id]
        amended_count = record.count_fp if new_count_fp is None else new_count_fp
        amendment = LimitOrderRequest.from_mapping(
            {
                "market_ticker": record.market_ticker,
                "side": record.side,
                "count_fp": amended_count,
                "limit_price_dollars": new_limit_price_dollars,
                "type": "limit",
                "client_order_id": client_order_id,
            }
        )
        self._validate_limit_workflow(amendment, reference_price_dollars)
        response = await self.client.amend_order(
            record.order_id,
            {
                "count": str(amendment.count_fp),
                "yes_price": str(amendment.limit_price_dollars),
            },
        )
        order_data = response.get("order", response)
        record.limit_price_dollars = amendment.limit_price_dollars
        record.count_fp = amendment.count_fp
        record.status = str(order_data.get("status", record.status))
        record.raw = order_data
        return record

    async def cancel_order(self, *, client_order_id: str) -> OrderRecord:
        record = self._records_by_client_id[client_order_id]
        response = await self.client.cancel_order(record.order_id)
        order_data = response.get("order", response)
        record.status = str(order_data.get("status", "cancelled"))
        record.raw = order_data
        return record

    async def reconcile_open_orders(self) -> list[OrderRecord]:
        response = await self.client.list_open_orders()
        orders = response.get("orders", [])
        open_by_id = {str(o.get("client_order_id")): o for o in orders if o.get("client_order_id")}

        for client_id, record in self._records_by_client_id.items():
            if client_id in open_by_id:
                data = open_by_id[client_id]
                record.status = str(data.get("status", "open"))
                record.raw = data
            elif record.status == "open":
                record.status = "unknown"

        return list(self._records_by_client_id.values())
