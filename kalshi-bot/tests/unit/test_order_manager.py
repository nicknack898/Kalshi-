import asyncio
from decimal import Decimal

from app.execution.order_manager import OrderManager, SlippageGuardrails
from app.schemas.risk import RiskDecision


class FakeREST:
    def __init__(self):
        self.calls = []

    async def request(self, method, path, *, params=None, json=None, authenticated=True):
        self.calls.append({"method": method, "path": path, "json": json, "authenticated": authenticated})
        return {"ok": True, "echo": json}


def test_place_limit_order_uses_side_specific_price_field() -> None:
    rest = FakeREST()
    manager = OrderManager(rest, SlippageGuardrails(max_slippage_dollars=Decimal("0.02")))
    decision = RiskDecision(
        approved=True,
        side="yes",
        size_fp=Decimal("10"),
        limit_price_dollars=Decimal("0.44"),
        max_price_dollars=Decimal("0.45"),
    )

    result = asyncio.run(manager.place_limit_order(ticker="KXTEST", decision=decision))

    assert result["ok"] is True
    payload = rest.calls[0]["json"]
    assert payload["yes_price_dollars"] == "0.44"
    assert "no_price_dollars" not in payload


def test_amend_order_rejects_non_positive_size() -> None:
    rest = FakeREST()
    manager = OrderManager(rest, SlippageGuardrails(max_slippage_dollars=Decimal("0.02")))

    try:
        asyncio.run(manager.amend_order("id", new_count_fp=Decimal("0")))
    except ValueError as exc:
        assert "positive" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
