from decimal import Decimal


def kelly_yes(p_model: Decimal, yes_price: Decimal) -> Decimal:
    if yes_price >= Decimal("1"):
        return Decimal("0")
    return (p_model - yes_price) / (Decimal("1") - yes_price)


def kelly_no(p_model: Decimal, no_price: Decimal) -> Decimal:
    if no_price >= Decimal("1"):
        return Decimal("0")
    return ((Decimal("1") - p_model) - no_price) / (Decimal("1") - no_price)


def edge_yes(p_model: Decimal, yes_price: Decimal) -> Decimal:
    return p_model - yes_price


def edge_no(p_model: Decimal, no_price: Decimal) -> Decimal:
    return (Decimal("1") - p_model) - no_price
