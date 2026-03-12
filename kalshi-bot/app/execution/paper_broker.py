from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4


@dataclass
class PaperOrder:
    order_id: str
    ticker: str
    side: str
    size_fp: Decimal
    limit_price_dollars: Decimal
    status: str


class PaperBroker:
    def __init__(self) -> None:
        self.orders: dict[str, PaperOrder] = {}

    def place_limit_order(self, *, ticker: str, side: str, size_fp: Decimal, limit_price_dollars: Decimal) -> PaperOrder:
        order = PaperOrder(
            order_id=str(uuid4()),
            ticker=ticker,
            side=side,
            size_fp=size_fp,
            limit_price_dollars=limit_price_dollars,
            status="resting",
        )
        self.orders[order.order_id] = order
        return order

    def cancel(self, order_id: str) -> None:
        if order_id in self.orders:
            self.orders[order_id].status = "cancelled"
