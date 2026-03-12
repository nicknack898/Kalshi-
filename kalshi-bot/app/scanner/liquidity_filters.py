from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from app.schemas.markets import MarketSnapshot


@dataclass
class LiquidityRules:
    min_volume_fp: Decimal = Decimal("200")
    max_spread_dollars: Decimal = Decimal("0.05")
    min_minutes_to_close: int = 15


def passes_filters(market: MarketSnapshot, rules: LiquidityRules) -> bool:
    if market.status.lower() != "open":
        return False
    if market.volume_fp < rules.min_volume_fp:
        return False
    now_ts = int(datetime.now(tz=timezone.utc).timestamp())
    if market.close_ts - now_ts < rules.min_minutes_to_close * 60:
        return False
    if market.yes_bid_dollars is not None and market.no_bid_dollars is not None:
        inferred_yes_ask = Decimal("1") - market.no_bid_dollars
        spread = inferred_yes_ask - market.yes_bid_dollars
        if spread > rules.max_spread_dollars:
            return False
    return True
