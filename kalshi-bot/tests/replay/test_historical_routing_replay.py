from datetime import datetime, timezone

import asyncio

from app.clients.historical_router import HistoricalRouter


class ReplayClient:
    def __init__(self, source: str, cutoff: str | None = None):
        self.source = source
        self.cutoff = cutoff
        self.events = []

    async def request(self, method, path, *, params=None, json=None):
        self.events.append((method, path, params or {}))
        if path == "/historical/cutoff":
            return {"cutoff": self.cutoff}
        return {"source": self.source, "path": path, "params": params or {}}


def test_replay_routes_boundary_timestamp_to_historical() -> None:
    live = ReplayClient("live", cutoff="2024-03-01T10:00:00Z")
    historical = ReplayClient("historical")
    router = HistoricalRouter(live_client=live, historical_client=historical)

    at_boundary = asyncio.run(router.request("GET", "/events", params={"timestamp": "2024-03-01T10:00:00Z"}))
    after_boundary = asyncio.run(router.request("GET", "/events", params={"timestamp": "2024-03-01T10:00:01Z"}))

    assert at_boundary["source"] == "historical"
    assert after_boundary["source"] == "live"
