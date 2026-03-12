import asyncio

from app.clients.kalshi_auth import KalshiAuth
from app.clients.kalshi_rest import KalshiRESTClient


class FlakyHTTPClient:
    def __init__(self) -> None:
        self.calls = 0

    async def request(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("temporary")
        return _Response({"ok": True})

    async def aclose(self):
        return None


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_request_retries_and_succeeds() -> None:
    client = KalshiRESTClient(base_url="https://example.com", auth=KalshiAuth("k", "s"))
    client._client = FlakyHTTPClient()

    result = asyncio.run(client.request("GET", "/markets", authenticated=False, max_attempts=2))

    assert result == {"ok": True}
    assert client._client.calls == 2
