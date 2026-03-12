from __future__ import annotations

import base64
import hmac
import time
from dataclasses import dataclass
from hashlib import sha256
from urllib.parse import urlsplit


@dataclass(slots=True)
class KalshiAuth:
    access_key: str
    signing_key: str

    def _signature_payload(self, method: str, url_or_path: str, timestamp_ms: int) -> str:
        path = urlsplit(url_or_path).path if "://" in url_or_path else url_or_path
        return f"{timestamp_ms}{method.upper()}{path}"

    def sign(self, method: str, url_or_path: str, timestamp_ms: int | None = None) -> dict[str, str]:
        ts = int(time.time() * 1000) if timestamp_ms is None else int(timestamp_ms)
        payload = self._signature_payload(method, url_or_path, ts)
        signature = hmac.new(
            self.signing_key.encode("utf-8"), payload.encode("utf-8"), sha256
        ).digest()
        b64_signature = base64.b64encode(signature).decode("utf-8")

        return {
            "KALSHI-ACCESS-KEY": self.access_key,
            "KALSHI-ACCESS-TIMESTAMP": str(ts),
            "KALSHI-ACCESS-SIGNATURE": b64_signature,
        }
