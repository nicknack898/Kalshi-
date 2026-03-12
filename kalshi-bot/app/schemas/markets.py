from decimal import Decimal

from pydantic import BaseModel


class MarketSnapshot(BaseModel):
    ticker: str
    status: str
    yes_bid_dollars: Decimal | None = None
    no_bid_dollars: Decimal | None = None
    volume_fp: Decimal
    close_ts: int
    fractional_trading_enabled: bool = False
