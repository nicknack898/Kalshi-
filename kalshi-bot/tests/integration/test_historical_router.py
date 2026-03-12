from datetime import datetime

import asyncio

from app.clients.historical_router import HistoricalRouter


class StubClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def request(self, method, path, *, params=None, json=None):
        self.calls.append({"method": method, "path": path, "params": params, "json": json})
        return self.responses.pop(0)


def test_router_uses_historical_for_old_timestamps() -> None:
    live = StubClient([{"cutoff": "2024-01-02T00:00:00Z"}])
    historical = StubClient([{"source": "historical"}])
    router = HistoricalRouter(live_client=live, historical_client=historical)

    response = asyncio.run(router.request("GET", "/markets", params={"timestamp": "2024-01-01T00:00:00Z"}))

    assert response["source"] == "historical"
    assert live.calls[0]["path"] == "/historical/cutoff"


def test_router_uses_live_for_recent_timestamps() -> None:
    live = StubClient([{"cutoff": "2024-01-02T00:00:00Z"}, {"source": "live"}])
    historical = StubClient([])
    router = HistoricalRouter(live_client=live, historical_client=historical)

    response = asyncio.run(router.request("GET", "/markets", params={"timestamp": "2024-01-03T00:00:00Z"}))

    assert response["source"] == "live"


def test_router_merge_mode_combines_datasets() -> None:
    live = StubClient([{"items": [{"id": 2}], "meta": {"l": 1}}])
    historical = StubClient([{"items": [{"id": 1}], "meta": {"h": 1}}])
    router = HistoricalRouter(live_client=live, historical_client=historical)

    merged = asyncio.run(router.request("GET", "/markets", params={"merged_dataset": True}))

    assert merged["items"] == [{"id": 1}, {"id": 2}]
    assert merged["meta"] == {"h": 1, "l": 1}
