from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, AsyncIterator

import websockets
from websockets.asyncio.client import ClientConnection

from app.clients.kalshi_auth import KalshiAuth


@dataclass(slots=True)
class KalshiWebSocketClient:
    ws_url: str
    auth: KalshiAuth

    def _auth_headers(self) -> dict[str, str]:
        return self.auth.sign("GET", "/trade-api/ws/v2")

    async def connect(self) -> ClientConnection:
        return await websockets.connect(self.ws_url, additional_headers=self._auth_headers())

    async def subscribe(
        self,
        conn: ClientConnection,
        *,
        channels: list[str],
        market_tickers: list[str] | None = None,
    ) -> None:
        msg: dict[str, Any] = {
            "id": 1,
            "cmd": "subscribe",
            "params": {"channels": channels},
        }
        if market_tickers:
            msg["params"]["market_tickers"] = market_tickers
        await conn.send(json.dumps(msg))

    async def stream_messages(self, conn: ClientConnection) -> AsyncIterator[dict[str, Any]]:
        async for raw in conn:
            yield json.loads(raw)
