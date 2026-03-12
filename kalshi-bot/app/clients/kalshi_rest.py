from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import httpx

from app.clients.kalshi_auth import KalshiAuth


@dataclass(slots=True)
class KalshiRESTClient:
    base_url: str
    auth: KalshiAuth
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=self.timeout_seconds)

    async def close(self) -> None:
        await self._client.aclose()

    def _build_url(self, path: str) -> str:
        normalized_path = path if path.startswith("/") else f"/{path}"
        return urljoin(self.base_url.rstrip("/") + "/", normalized_path.lstrip("/"))

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = self._build_url(path)
        headers = self.auth.sign(method, path)
        response = await self._client.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json,
            headers=headers,
        )
        response.raise_for_status()
        if not response.content:
            return {}
        return response.json()

    async def get_market(self, ticker: str) -> dict[str, Any]:
        return await self.request("GET", f"/trade-api/v2/markets/{ticker}")

    async def create_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request("POST", "/trade-api/v2/portfolio/orders", json=payload)

    async def amend_order(self, order_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request("POST", f"/trade-api/v2/portfolio/orders/{order_id}/amend", json=payload)

    async def cancel_order(self, order_id: str) -> dict[str, Any]:
        return await self.request("DELETE", f"/trade-api/v2/portfolio/orders/{order_id}")

    async def list_open_orders(self) -> dict[str, Any]:
        return await self.request("GET", "/trade-api/v2/portfolio/orders", params={"status": "open"})
