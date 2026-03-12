from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.clients.kalshi_rest import KalshiRESTClient


@dataclass(slots=True)
class HistoricalRouter:
    live_client: KalshiRESTClient
    historical_client: KalshiRESTClient
    cutoff_path: str = "/historical/cutoff"
    _cutoff: datetime | None = field(default=None, init=False)

    @staticmethod
    def _parse_dt(value: str | datetime | None) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)

    async def refresh_cutoff(self) -> datetime:
        payload = await self.live_client.request("GET", self.cutoff_path)
        cutoff = self._parse_dt(payload.get("cutoff") or payload.get("cutoff_time"))
        if cutoff is None:
            raise ValueError("historical cutoff endpoint did not return cutoff timestamp")
        self._cutoff = cutoff
        return cutoff

    async def get_cutoff(self) -> datetime:
        if self._cutoff is None:
            return await self.refresh_cutoff()
        return self._cutoff

    async def should_route_historical(self, params: dict[str, Any] | None = None) -> bool:
        params = params or {}
        candidate_ts: datetime | None = None
        for key in ("timestamp", "start_ts", "end_ts"):
            if key in params:
                candidate_ts = self._parse_dt(params[key])
                if candidate_ts:
                    break
        if candidate_ts is None:
            return False

        cutoff = await self.get_cutoff()
        return candidate_ts <= cutoff

    @staticmethod
    def _merge_payloads(historical: dict[str, Any], live: dict[str, Any]) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        all_keys = set(historical) | set(live)
        for key in all_keys:
            h_value = historical.get(key)
            l_value = live.get(key)
            if isinstance(h_value, list) and isinstance(l_value, list):
                merged[key] = h_value + l_value
            elif isinstance(h_value, dict) and isinstance(l_value, dict):
                merged[key] = {**h_value, **l_value}
            else:
                merged[key] = l_value if l_value is not None else h_value
        return merged

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = dict(params or {})
        merged_dataset = bool(params.pop("merged_dataset", False))

        if merged_dataset:
            historical = await self.historical_client.request(method, path, params=params, json=json)
            live = await self.live_client.request(method, path, params=params, json=json)
            return self._merge_payloads(historical, live)

        if await self.should_route_historical(params=params):
            return await self.historical_client.request(method, path, params=params, json=json)
        return await self.live_client.request(method, path, params=params, json=json)


def cents_to_decimal_str(price_cents: int | str | Decimal) -> tuple[str, Decimal]:
    cents = Decimal(str(price_cents))
    dollars = cents / Decimal("100")
    as_str = format(dollars, "f")
    return as_str, dollars
