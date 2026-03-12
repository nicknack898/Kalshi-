from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


class SchemaValidationError(ValueError):
    """Raised when schema values cannot be parsed or validated."""


def parse_decimal(value: Any, *, field_name: str) -> Decimal:
    """Parse a value into Decimal with strict validation."""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        # Avoid binary float artifacts by using string conversion.
        value = str(value)
    if isinstance(value, str):
        try:
            parsed = Decimal(value)
        except InvalidOperation as exc:
            raise SchemaValidationError(f"Invalid decimal for {field_name}: {value!r}") from exc
        if parsed.is_nan() or parsed.is_infinite():
            raise SchemaValidationError(f"Non-finite decimal for {field_name}: {value!r}")
        return parsed

    raise SchemaValidationError(f"Unsupported type for {field_name}: {type(value).__name__}")


@dataclass(slots=True)
class FixedPointSchema:
    """Common schema utilities with Decimal-based fixed-point field validation."""

    @classmethod
    def validate_fixed_point_fields(cls, payload: Mapping[str, Any]) -> dict[str, Any]:
        validated: dict[str, Any] = {}
        for key, value in payload.items():
            if key.endswith("_dollars") or key.endswith("_fp"):
                validated[key] = parse_decimal(value, field_name=key)
            else:
                validated[key] = value
        return validated
