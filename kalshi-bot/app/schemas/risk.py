from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(slots=True)
class RiskDecision:
    approved: bool
    side: str
    size_fp: Decimal
    limit_price_dollars: Decimal
    max_price_dollars: Decimal
    reason_codes: list[str] = field(default_factory=list)
    kelly_raw: Decimal = Decimal("0")
    kelly_fractional: Decimal = Decimal("0")
    risk_snapshot: dict = field(default_factory=dict)
