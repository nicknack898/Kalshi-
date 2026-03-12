from decimal import Decimal

from app.risk.engine import RiskConfig, RiskEngine, TradeContext


def _trade(**overrides):
    base = dict(
        market_ticker="TEST",
        model_price_dollars=Decimal("0.60"),
        order_price_dollars=Decimal("0.30"),
        fees_dollars=Decimal("0.001"),
        estimated_win_prob=Decimal("0.75"),
        bankroll_dollars=Decimal("1000"),
        requested_notional_dollars=Decimal("50"),
        current_total_exposure_dollars=Decimal("100"),
        daily_pnl_dollars=Decimal("100"),
        drawdown_dollars=Decimal("50"),
        exchange_healthy=True,
        state_age_seconds=1,
    )
    base.update(overrides)
    return TradeContext(**base)


def test_ev_and_kelly_generate_positive_approval() -> None:
    engine = RiskEngine(RiskConfig())
    decision = engine.evaluate(_trade())
    assert decision.approved is True
    assert decision.max_size_dollars > Decimal("0")


def test_risk_limits_block_when_exposure_and_losses_breach() -> None:
    engine = RiskEngine(RiskConfig(max_total_exposure_dollars=Decimal("120"), max_daily_loss_dollars=Decimal("10")))
    decision = engine.evaluate(
        _trade(
            current_total_exposure_dollars=Decimal("100"),
            requested_notional_dollars=Decimal("30"),
            daily_pnl_dollars=Decimal("-15"),
        )
    )
    assert decision.approved is False
    assert "Order exceeds total exposure cap" in decision.blockers
    assert "Daily loss limit breached" in decision.blockers
