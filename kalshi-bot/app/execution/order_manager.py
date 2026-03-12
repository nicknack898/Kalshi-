from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4

from app.clients.kalshi_rest import KalshiRESTClient
from app.schemas.risk import RiskDecision


@dataclass(slots=True)
class SlippageGuardrails:
    max_slippage_dollars: Decimal


@dataclass(slots=True)
class OrderRecord:
    order_id: str
    client_order_id: str
    status: str
    raw: dict


class OrderManager:
    """Risk-gated limit-order manager."""

    def __init__(self, rest_client: KalshiRESTClient, guardrails: SlippageGuardrails) -> None:
        self.rest_client = rest_client
        self.guardrails = guardrails

    async def place_limit_order(self, *, ticker: str, decision: RiskDecision) -> dict:
        if not decision.approved:
            raise ValueError("Risk decision not approved")
        if decision.size_fp <= Decimal("0"):
            raise ValueError("Order size must be positive")
        if decision.side not in {"yes", "no"}:
            raise ValueError("side must be 'yes' or 'no'")
        if decision.limit_price_dollars < Decimal("0") or decision.limit_price_dollars > Decimal("1"):
            raise ValueError("Limit price must be in [0, 1]")
        if decision.limit_price_dollars > decision.max_price_dollars:
            raise ValueError("Limit price exceeds approved max price")
        if (decision.max_price_dollars - decision.limit_price_dollars) > self.guardrails.max_slippage_dollars:
            raise ValueError("Price exceeds slippage guardrail")

        client_order_id = str(uuid4())
        payload = {
            "ticker": ticker,
            "client_order_id": client_order_id,
            "side": decision.side,
            "action": "buy",
            "count_fp": str(decision.size_fp),
            # Intentionally omit removed legacy `type` field.
            "yes_price_dollars": str(decision.limit_price_dollars) if decision.side == "yes" else None,
            "no_price_dollars": str(decision.limit_price_dollars) if decision.side == "no" else None,
        }
        clean_payload = {k: v for k, v in payload.items() if v is not None}
        return await self.rest_client.request("POST", "/portfolio/orders", json=clean_payload)

    async def amend_order(self, order_id: str, *, new_count_fp: Decimal) -> dict:
        if new_count_fp <= Decimal("0"):
            raise ValueError("new_count_fp must be positive")
        return await self.rest_client.request(
            "POST",
            f"/portfolio/orders/{order_id}/amend",
            json={"count_fp": str(new_count_fp)},
        )

    async def cancel_order(self, order_id: str) -> dict:
        return await self.rest_client.request("DELETE", f"/portfolio/orders/{order_id}")


__all__ = ["OrderManager", "OrderRecord", "SlippageGuardrails"]
