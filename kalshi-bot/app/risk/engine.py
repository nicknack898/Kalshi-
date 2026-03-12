from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from app.risk.kelly import edge_no, edge_yes, kelly_no, kelly_yes
from app.schemas.risk import RiskDecision


@dataclass(slots=True)
class RiskConfig:
    fractional_kelly: Decimal = Decimal("0.25")
    edge_threshold: Decimal = Decimal("0.04")
    max_single_position_pct: Decimal = Decimal("0.05")
    max_total_open_exposure_pct: Decimal = Decimal("0.30")
    min_expected_profit_dollars: Decimal = Decimal("5.00")
    stop_file_path: str = "./STOP"


@dataclass(slots=True)
class TradeContext:
    bankroll: Decimal
    open_exposure: Decimal
    max_contracts: Decimal
    estimated_cost_per_contract: Decimal = Decimal("0")


class RiskEngine:
    def __init__(self, config: RiskConfig) -> None:
        self.config = config

    def evaluate(self, *, side: str, p_model: Decimal, price: Decimal, context: TradeContext) -> RiskDecision:
        reasons: list[str] = []
        if Path(self.config.stop_file_path).exists():
            reasons.append("stop_file_present")

        if side == "yes":
            edge = edge_yes(p_model, price)
            k_raw = kelly_yes(p_model, price)
        else:
            edge = edge_no(p_model, price)
            k_raw = kelly_no(p_model, price)

        if edge < self.config.edge_threshold:
            reasons.append("edge_below_threshold")

        k_frac = max(Decimal("0"), k_raw * self.config.fractional_kelly)
        at_risk = context.bankroll * k_frac
        capped = min(at_risk, context.bankroll * self.config.max_single_position_pct, context.max_contracts)

        expected_profit = edge * capped - context.estimated_cost_per_contract * capped
        if expected_profit <= Decimal("0"):
            reasons.append("non_positive_net_ev")
        if expected_profit < self.config.min_expected_profit_dollars:
            reasons.append("expected_profit_below_minimum")

        if context.open_exposure + capped > context.bankroll * self.config.max_total_open_exposure_pct:
            reasons.append("global_exposure_cap")

        approved = len(reasons) == 0
        return RiskDecision(
            approved=approved,
            side=side,
            size_fp=capped if approved else Decimal("0"),
            limit_price_dollars=price,
            max_price_dollars=price,
            reason_codes=reasons,
            kelly_raw=k_raw,
            kelly_fractional=k_frac,
            risk_snapshot={"edge": str(edge), "expected_profit": str(expected_profit)},
        )


# Backward-compatible helper

def evaluate_buy(
    *,
    side: str,
    p_model: Decimal,
    price: Decimal,
    bankroll: Decimal,
    max_contracts: Decimal,
    estimated_cost_per_contract: Decimal,
    context,
) -> RiskDecision:
    cfg = RiskConfig(
        fractional_kelly=context.fractional_kelly,
        edge_threshold=context.edge_threshold,
        max_single_position_pct=context.max_single_position_pct,
        max_total_open_exposure_pct=context.max_total_open_exposure_pct,
        min_expected_profit_dollars=context.min_expected_profit_dollars,
        stop_file_path=context.stop_file_path,
    )
    engine = RiskEngine(cfg)
    return engine.evaluate(
        side=side,
        p_model=p_model,
        price=price,
        context=TradeContext(
            bankroll=bankroll,
            open_exposure=context.open_exposure,
            max_contracts=max_contracts,
            estimated_cost_per_contract=estimated_cost_per_contract,
        ),
    )


@dataclass
class RiskContext:
    bankroll: Decimal
    open_exposure: Decimal
    max_single_position_pct: Decimal
    max_total_open_exposure_pct: Decimal
    fractional_kelly: Decimal
    edge_threshold: Decimal
    min_expected_profit_dollars: Decimal
    stop_file_path: str
