import asyncio

from app.clients.kalshi_auth import KalshiAuth
from app.clients.kalshi_rest import KalshiRESTClient


class FakePagedClient(KalshiRESTClient):
    def __post_init__(self) -> None:  # noqa: D401
        self.calls = []

    async def request(self, method: str, path: str, *, params=None, json=None):
        self.calls.append(params.copy() if params else {})
        cursor = (params or {}).get("cursor")
        if cursor is None:
            return {"markets": [{"ticker": "A"}], "next_cursor": "c2"}
        if cursor == "c2":
            return {"markets": [{"ticker": "B"}], "next_cursor": None}
        return {"markets": []}


def test_paginate_fetches_all_pages() -> None:
    client = FakePagedClient(base_url="https://example.com", auth=KalshiAuth("a", "b"))
    items = asyncio.run(client.paginate("/trade-api/v2/markets"))
    assert [item["ticker"] for item in items] == ["A", "B"]
    assert client.calls == [{}, {"cursor": "c2"}]
