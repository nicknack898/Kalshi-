from app.schemas.markets import MarketSnapshot
from app.scanner.liquidity_filters import LiquidityRules, passes_filters


class MarketScanner:
    def __init__(self, rules: LiquidityRules | None = None) -> None:
        self.rules = rules or LiquidityRules()

    def scan(self, markets: list[MarketSnapshot]) -> list[MarketSnapshot]:
        return [m for m in markets if passes_filters(m, self.rules)]
