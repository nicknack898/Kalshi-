from decimal import Decimal

from pydantic import BaseModel


class ForecastSignal(BaseModel):
    ticker: str
    p_model: Decimal
    confidence_score: Decimal
    edge_yes: Decimal
    edge_no: Decimal
