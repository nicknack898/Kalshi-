from __future__ import annotations

import base64
import hashlib
import hmac
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SignedHeaders:
    key: str
    timestamp: str
    signature: str


@dataclass(slots=True)
class KalshiAuth:
    access_key: str
    signing_key: str

    def sign(self, method: str, path: str, *, timestamp_ms: int) -> dict[str, str]:
        signature = sign_request(
            timestamp=str(timestamp_ms),
            method=method,
            path=path,
            signing_key=self.signing_key,
        )
        return {
            "KALSHI-ACCESS-KEY": self.access_key,
            "KALSHI-ACCESS-TIMESTAMP": str(timestamp_ms),
            "KALSHI-ACCESS-SIGNATURE": signature,
        }


def build_signature_payload(timestamp: str, method: str, path: str) -> str:
    normalized_path = path.split("?", 1)[0]
    return f"{timestamp}{method.upper()}{normalized_path}"


def sign_request(
    *,
    timestamp: str,
    method: str,
    path: str,
    signing_key: str | None = None,
    private_key_path: str | None = None,
) -> str:
    payload = build_signature_payload(timestamp, method, path).encode("utf-8")
    if signing_key is None:
        if private_key_path is None:
            raise ValueError("Either signing_key or private_key_path must be provided")
        signing_key = Path(private_key_path).read_text(encoding="utf-8")

    return base64.b64encode(
        hmac.new(signing_key.encode("utf-8"), payload, hashlib.sha256).digest()
    ).decode("utf-8")


def build_auth_headers(
    *, key_id: str, timestamp: str, method: str, path: str, private_key_path: str
) -> SignedHeaders:
    signature = sign_request(
        timestamp=timestamp,
        method=method,
        path=path,
        private_key_path=private_key_path,
    )
    return SignedHeaders(key=key_id, timestamp=timestamp, signature=signature)
