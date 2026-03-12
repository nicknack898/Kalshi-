from decimal import Decimal

from app.risk.engine import RiskContext, evaluate_buy


def test_risk_approves_positive_ev(tmp_path) -> None:
    context = RiskContext(
        bankroll=Decimal("1000"),
        open_exposure=Decimal("0"),
        max_single_position_pct=Decimal("0.05"),
        max_total_open_exposure_pct=Decimal("0.30"),
        fractional_kelly=Decimal("0.25"),
        edge_threshold=Decimal("0.04"),
        min_expected_profit_dollars=Decimal("1"),
        stop_file_path=str(tmp_path / "STOP"),
    )
    decision = evaluate_buy(
        side="yes",
        p_model=Decimal("0.60"),
        price=Decimal("0.50"),
        bankroll=Decimal("1000"),
        max_contracts=Decimal("100"),
        estimated_cost_per_contract=Decimal("0.01"),
        context=context,
    )
    assert decision.approved


def test_risk_blocks_stop_file(tmp_path) -> None:
    stop = tmp_path / "STOP"
    stop.write_text("halt")
    context = RiskContext(
        bankroll=Decimal("1000"),
        open_exposure=Decimal("0"),
        max_single_position_pct=Decimal("0.05"),
        max_total_open_exposure_pct=Decimal("0.30"),
        fractional_kelly=Decimal("0.25"),
        edge_threshold=Decimal("0.04"),
        min_expected_profit_dollars=Decimal("1"),
        stop_file_path=str(stop),
    )
    decision = evaluate_buy(
        side="yes",
        p_model=Decimal("0.60"),
        price=Decimal("0.50"),
        bankroll=Decimal("1000"),
        max_contracts=Decimal("100"),
        estimated_cost_per_contract=Decimal("0.01"),
        context=context,
    )
    assert not decision.approved
    assert "stop_file_present" in decision.reason_codes
