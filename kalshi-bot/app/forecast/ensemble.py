from decimal import Decimal

from app.risk.kelly import edge_no, edge_yes
from app.schemas.signals import ForecastSignal


class EnsembleForecaster:
    def forecast(self, *, ticker: str, p_model: Decimal, confidence: Decimal, yes_price: Decimal, no_price: Decimal) -> ForecastSignal:
        return ForecastSignal(
            ticker=ticker,
            p_model=p_model,
            confidence_score=confidence,
            edge_yes=edge_yes(p_model, yes_price),
            edge_no=edge_no(p_model, no_price),
        )
