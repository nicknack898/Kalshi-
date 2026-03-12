from decimal import Decimal

from app.schemas.orderbook import convert_orderbook_levels


def test_convert_orderbook_levels_to_decimal_and_string() -> None:
    converted = convert_orderbook_levels([
        {"price_cents": 44, "count": "12"},
        {"price_cents": "57", "count": 3},
    ])
    assert converted[0]["price"] == Decimal("0.44")
    assert converted[0]["price_str"] == "0.44"
    assert converted[1]["count"] == Decimal("3")
    assert converted[1]["count_str"] == "3"
