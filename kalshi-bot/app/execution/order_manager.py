from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from app.clients.kalshi_rest import KalshiRESTClient
from app.schemas.risk import RiskDecision


class OrderManager:
    def __init__(self, rest_client: KalshiRESTClient) -> None:
        self.rest_client = rest_client

    def place_limit_order(self, *, ticker: str, decision: RiskDecision) -> dict:
        if not decision.approved:
            raise ValueError("Risk decision not approved")
        payload = {
            "ticker": ticker,
            "client_order_id": str(uuid4()),
            "side": decision.side,
            "action": "buy",
            "count_fp": str(decision.size_fp),
            "yes_price_dollars": str(decision.limit_price_dollars) if decision.side == "yes" else None,
            "no_price_dollars": str(decision.limit_price_dollars) if decision.side == "no" else None,
        }
        clean_payload = {k: v for k, v in payload.items() if v is not None}
        return self.rest_client.request("POST", "/portfolio/orders", json=clean_payload)

    def amend_order(self, order_id: str, *, new_count_fp: Decimal) -> dict:
        return self.rest_client.request("POST", f"/portfolio/orders/{order_id}/amend", json={"count_fp": str(new_count_fp)})

    def cancel_order(self, order_id: str) -> dict:
        return self.rest_client.request("DELETE", f"/portfolio/orders/{order_id}")
