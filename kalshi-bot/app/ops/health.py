from __future__ import annotations

from dataclasses import dataclass

from app.clients.kalshi_rest import KalshiRESTClient


@dataclass(slots=True)
class ExchangeHealth:
    exchange_open: bool
    in_maintenance: bool
    status: str

    @property
    def healthy_for_trading(self) -> bool:
        return self.exchange_open and not self.in_maintenance and self.status.lower() == "open"


async def fetch_exchange_health(rest_client: KalshiRESTClient) -> ExchangeHealth:
    status_payload = await rest_client.request("GET", "/exchange/status", authenticated=False)
    schedule_payload = await rest_client.request("GET", "/exchange/schedule", authenticated=False)

    status = str(status_payload.get("exchange_status") or status_payload.get("status") or "unknown")
    exchange_open = bool(status_payload.get("is_open", status.lower() == "open"))
    in_maintenance = bool(
        schedule_payload.get("is_maintenance", False)
        or status_payload.get("in_maintenance", False)
        or status_payload.get("maintenance", False)
    )

    return ExchangeHealth(
        exchange_open=exchange_open,
        in_maintenance=in_maintenance,
        status=status,
    )
"""Module scaffold."""
