from __future__ import annotations

import json
import time
from collections.abc import Iterable
from typing import Any

import websockets

from app.clients.kalshi_auth import KalshiAuth
from app.constants import DEMO_WS_BASE, PROD_WS_BASE


class KalshiWsClient:
    def __init__(
        self,
        *,
        env: str = "demo",
        api_key_id: str,
        signing_key: str,
    ) -> None:
        self.url = DEMO_WS_BASE if env == "demo" else PROD_WS_BASE
        self.auth = KalshiAuth(access_key=api_key_id, signing_key=signing_key)

    async def connect_and_subscribe(self, channels: Iterable[str]) -> Any:
        timestamp_ms = int(time.time() * 1000)
        headers = self.auth.sign("GET", "/trade-api/ws/v2", timestamp_ms=timestamp_ms)
        websocket = await websockets.connect(self.url, additional_headers=headers)
        await websocket.send(json.dumps({"type": "subscribe", "channels": list(channels)}))
        return websocket


KalshiWSClient = KalshiWsClient
