import asyncio

from app.ops.health import fetch_exchange_health


class FakeREST:
    async def request(self, method, path, *, params=None, json=None, authenticated=True):
        if path == "/exchange/status":
            return {"status": "open", "is_open": True}
        if path == "/exchange/schedule":
            return {"is_maintenance": False}
        return {}


def test_fetch_exchange_health_marks_healthy() -> None:
    health = asyncio.run(fetch_exchange_health(FakeREST()))
    assert health.healthy_for_trading
