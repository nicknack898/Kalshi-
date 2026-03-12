from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from app.schemas.fixed_point import FixedPointSchema, SchemaValidationError, parse_decimal


@dataclass(slots=True)
class Quote(FixedPointSchema):
    ticker: str
    bid_dollars: Decimal
    ask_dollars: Decimal
    last_dollars: Decimal | None = None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "Quote":
        data = cls.validate_fixed_point_fields(payload)
        ticker = data.get("ticker")
        if not ticker:
            raise SchemaValidationError("Quote missing required field: ticker")
        return cls(
            ticker=str(ticker),
            bid_dollars=parse_decimal(data.get("bid_dollars"), field_name="bid_dollars"),
            ask_dollars=parse_decimal(data.get("ask_dollars"), field_name="ask_dollars"),
            last_dollars=(
                parse_decimal(data["last_dollars"], field_name="last_dollars")
                if data.get("last_dollars") is not None
                else None
            ),
        )


@dataclass(slots=True)
class LimitOrderRequest(FixedPointSchema):
    market_ticker: str
    side: str
    count_fp: Decimal
    limit_price_dollars: Decimal
    client_order_id: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "LimitOrderRequest":
        data = cls.validate_fixed_point_fields(payload)
        side = str(data.get("side", "")).lower()
        if side not in {"buy", "sell"}:
            raise SchemaValidationError("side must be 'buy' or 'sell'")

        if str(data.get("type", "limit")).lower() != "limit":
            raise SchemaValidationError("Only limit orders are supported")

        return cls(
            market_ticker=str(data["market_ticker"]),
            side=side,
            count_fp=parse_decimal(data["count_fp"], field_name="count_fp"),
            limit_price_dollars=parse_decimal(
                data["limit_price_dollars"], field_name="limit_price_dollars"
            ),
            client_order_id=str(data["client_order_id"]),
        )
