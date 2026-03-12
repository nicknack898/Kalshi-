from __future__ import annotations

from decimal import Decimal
from typing import Iterable


def convert_orderbook_levels(levels: Iterable[dict[str, str | int]]) -> list[dict[str, Decimal | str]]:
    converted: list[dict[str, Decimal | str]] = []
    for level in levels:
        price_cents = Decimal(str(level["price_cents"]))
        count = Decimal(str(level["count"]))
        price = price_cents / Decimal("100")
        converted.append(
            {
                "price_str": format(price, "f"),
                "price": price,
                "count_str": format(count, "f"),
                "count": count,
            }
        )
    return converted
