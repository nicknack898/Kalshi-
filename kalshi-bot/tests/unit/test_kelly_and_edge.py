from decimal import Decimal

from app.risk.kelly import edge_no, edge_yes, kelly_no, kelly_yes


def test_edge_math() -> None:
    p = Decimal("0.60")
    assert edge_yes(p, Decimal("0.50")) == Decimal("0.10")
    assert edge_no(p, Decimal("0.30")) == Decimal("0.10")


def test_kelly_math() -> None:
    p = Decimal("0.60")
    assert kelly_yes(p, Decimal("0.50")) == Decimal("0.2")
    assert kelly_no(p, Decimal("0.30")) == Decimal("0.1428571428571428571428571429")
