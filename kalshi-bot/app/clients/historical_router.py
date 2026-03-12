from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class HistoricalRouter:
    live_client: Any
    historical_client: Any

    async def _get_cutoff(self) -> datetime:
        payload = await self.live_client.request("GET", "/historical/cutoff")
        cutoff = payload["cutoff"]
        return datetime.fromisoformat(cutoff.replace("Z", "+00:00")).astimezone(timezone.utc)

    async def request(self, method: str, path: str, *, params: dict | None = None, json: dict | None = None) -> dict:
        params = params or {}
        if params.get("merged_dataset"):
            historical = await self.historical_client.request(method, path, params=params, json=json)
            live = await self.live_client.request(method, path, params=params, json=json)
            return {
                "items": [*(historical.get("items", [])), *(live.get("items", []))],
                "meta": {**historical.get("meta", {}), **live.get("meta", {})},
            }

        timestamp = params.get("timestamp")
        if timestamp:
            cutoff = await self._get_cutoff()
            request_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone(timezone.utc)
            if request_time <= cutoff:
                return await self.historical_client.request(method, path, params=params, json=json)
        return await self.live_client.request(method, path, params=params, json=json)


from dataclasses import dataclass

@dataclass(frozen=True)
class RoutingDecision:
    use_historical: bool
    endpoint_path: str

def route_endpoint(*, base_path: str, query_start, cutoff_timestamp_ms: int) -> RoutingDecision:
    from datetime import datetime, timezone
    cutoff_dt = datetime.fromtimestamp(cutoff_timestamp_ms/1000, tz=timezone.utc)
    use_historical = query_start < cutoff_dt
    return RoutingDecision(use_historical=use_historical, endpoint_path=(f"/historical{base_path}" if use_historical else base_path))
