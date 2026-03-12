from decimal import Decimal

import pytest

from app.schemas.fixed_point import SchemaValidationError, parse_decimal


def test_parse_decimal_accepts_supported_types() -> None:
    assert parse_decimal("0.125", field_name="p") == Decimal("0.125")
    assert parse_decimal(2, field_name="p") == Decimal("2")
    assert parse_decimal(0.1, field_name="p") == Decimal("0.1")


def test_parse_decimal_rejects_non_finite() -> None:
    with pytest.raises(SchemaValidationError):
        parse_decimal("NaN", field_name="p")
