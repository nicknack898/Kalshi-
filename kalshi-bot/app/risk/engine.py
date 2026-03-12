from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class RiskConfig:
    min_edge_dollars: Decimal = Decimal("0.01")
    min_ev_after_costs_dollars: Decimal = Decimal("0")
    max_kelly_fraction: Decimal = Decimal("0.25")
    max_order_notional_dollars: Decimal = Decimal("250")
    max_total_exposure_dollars: Decimal = Decimal("2000")
    max_daily_loss_dollars: Decimal = Decimal("500")
    max_drawdown_dollars: Decimal = Decimal("1500")
    stale_state_seconds: int = 30
    stop_file_path: str = "/tmp/KALSHI_STOP"


@dataclass(slots=True)
class TradeContext:
    market_ticker: str
    model_price_dollars: Decimal
    order_price_dollars: Decimal
    fees_dollars: Decimal
    estimated_win_prob: Decimal
    bankroll_dollars: Decimal
    requested_notional_dollars: Decimal
    current_total_exposure_dollars: Decimal
    daily_pnl_dollars: Decimal
    drawdown_dollars: Decimal
    exchange_healthy: bool
    state_age_seconds: int


@dataclass(slots=True)
class RiskDecision:
    approved: bool
    blockers: list[str] = field(default_factory=list)
    max_size_dollars: Decimal = Decimal("0")


class RiskEngine:
    def __init__(self, config: RiskConfig | None = None) -> None:
        self.config = config or RiskConfig()

    def evaluate(self, trade: TradeContext) -> RiskDecision:
        blockers: list[str] = []

        if Path(self.config.stop_file_path).exists():
            blockers.append("STOP file present")

        if not trade.exchange_healthy:
            blockers.append("Exchange health check failed")

        if trade.state_age_seconds > self.config.stale_state_seconds:
            blockers.append("State is stale; fail-closed")

        edge = trade.model_price_dollars - trade.order_price_dollars
        if edge < self.config.min_edge_dollars:
            blockers.append("Insufficient edge")

        gross_ev = (trade.estimated_win_prob * edge) - ((Decimal("1") - trade.estimated_win_prob) * trade.order_price_dollars)
        ev_after_costs = gross_ev - trade.fees_dollars
        if ev_after_costs <= self.config.min_ev_after_costs_dollars:
            blockers.append("EV-after-costs below threshold")

        b = (Decimal("1") - trade.order_price_dollars) / trade.order_price_dollars
        p = trade.estimated_win_prob
        q = Decimal("1") - p
        kelly_fraction = ((b * p) - q) / b if b > 0 else Decimal("0")
        if kelly_fraction <= 0:
            blockers.append("Kelly sizing indicates no bet")

        capped_kelly_fraction = min(max(kelly_fraction, Decimal("0")), self.config.max_kelly_fraction)
        kelly_size_dollars = trade.bankroll_dollars * capped_kelly_fraction

        if trade.requested_notional_dollars > self.config.max_order_notional_dollars:
            blockers.append("Order exceeds per-order exposure cap")

        projected_exposure = trade.current_total_exposure_dollars + trade.requested_notional_dollars
        if projected_exposure > self.config.max_total_exposure_dollars:
            blockers.append("Order exceeds total exposure cap")

        if trade.daily_pnl_dollars <= -self.config.max_daily_loss_dollars:
            blockers.append("Daily loss limit breached")

        if trade.drawdown_dollars >= self.config.max_drawdown_dollars:
            blockers.append("Max drawdown breached")

        max_size = min(
            self.config.max_order_notional_dollars,
            max(kelly_size_dollars, Decimal("0")),
        )
        return RiskDecision(approved=not blockers, blockers=blockers, max_size_dollars=max_size)

    def assert_approved(self, trade: TradeContext) -> RiskDecision:
        decision = self.evaluate(trade)
        if not decision.approved:
            joined = "; ".join(decision.blockers)
            raise PermissionError(f"Risk check failed: {joined}")
        return decision

    @staticmethod
    def summarize_blockers(decision: RiskDecision) -> str:
        return ", ".join(decision.blockers) if decision.blockers else "none"

    @staticmethod
    def has_critical_blockers(decision: RiskDecision, patterns: Iterable[str]) -> bool:
        blockers = " ".join(decision.blockers).lower()
        return any(token.lower() in blockers for token in patterns)
