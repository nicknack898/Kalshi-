from __future__ import annotations

import json
import time

from websockets.sync.client import connect

from app.clients.kalshi_auth import build_auth_headers
from app.constants import DEMO_WS_BASE, PROD_WS_BASE


class KalshiWsClient:
    def __init__(self, *, env: str, api_key_id: str, private_key_path: str) -> None:
        self.url = DEMO_WS_BASE if env == "demo" else PROD_WS_BASE
        self.api_key_id = api_key_id
        self.private_key_path = private_key_path

    def connect_and_subscribe(self, channels: list[str]) -> None:
        ts = str(int(time.time() * 1000))
        auth = build_auth_headers(
            key_id=self.api_key_id,
            timestamp=ts,
            method="GET",
            path="/trade-api/ws/v2",
            private_key_path=self.private_key_path,
        )
        headers = {
            "KALSHI-ACCESS-KEY": auth.key,
            "KALSHI-ACCESS-TIMESTAMP": auth.timestamp,
            "KALSHI-ACCESS-SIGNATURE": auth.signature,
        }
        with connect(self.url, additional_headers=headers) as websocket:
            websocket.send(json.dumps({"type": "subscribe", "channels": channels}))
