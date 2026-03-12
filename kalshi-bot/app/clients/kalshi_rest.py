from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from app.clients.kalshi_auth import KalshiAuth
from app.constants import DEMO_REST_BASE, PROD_REST_BASE


class KalshiRESTClient:
    def __init__(
        self,
        base_url: str | None = None,
        auth: KalshiAuth | None = None,
        *,
        env: str = "demo",
        api_key_id: str | None = None,
        signing_key: str | None = None,
        timeout_seconds: int = 15,
    ) -> None:
        self.base_url = (base_url or (DEMO_REST_BASE if env == "demo" else PROD_REST_BASE)).rstrip("/")
        self.auth = auth or KalshiAuth(access_key=api_key_id or "", signing_key=signing_key or "")
        self._client = httpx.AsyncClient(timeout=timeout_seconds)

        post_init = getattr(self, "__post_init__", None)
        if callable(post_init):
            post_init()

    def _signed_headers(self, method: str, path: str) -> dict[str, str]:
        timestamp_ms = int(time.time() * 1000)
        return self.auth.sign(method, path, timestamp_ms=timestamp_ms)

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        authenticated: bool = True,
        max_attempts: int = 4,
    ) -> dict[str, Any]:
        normalized_path = path if path.startswith("/") else f"/{path}"
        url = f"{self.base_url}{normalized_path}"
        headers: dict[str, str] = self._signed_headers(method, normalized_path) if authenticated else {}

        delay = 0.2
        for attempt in range(1, max_attempts + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPStatusError, httpx.HTTPError, Exception):
                # local test stub may raise custom non-httpx exceptions; retry conservatively.
                if attempt == max_attempts:
                    raise
                await asyncio.sleep(delay)
                delay = min(delay * 2, 2.0)

        raise RuntimeError("unreachable")

    async def paginate(self, path: str, *, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        merged = dict(params or {})
        out: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            page_params = dict(merged)
            if cursor:
                page_params["cursor"] = cursor

            payload = await self.request("GET", path, params=page_params)

            if "markets" in payload:
                out.extend(payload["markets"])
            elif "events" in payload:
                out.extend(payload["events"])
            else:
                out.extend(payload.get("items", []))

            cursor = payload.get("cursor") or payload.get("next_cursor")
            if not cursor:
                break

        return out

    async def aclose(self) -> None:
        await self._client.aclose()


# Backward-compatible alias used by earlier modules.
KalshiRestClient = KalshiRESTClient
