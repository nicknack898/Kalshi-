from __future__ import annotations

from typing import Any


class KalshiRESTClient:
    def __init__(self, base_url: str, auth: Any) -> None:
        self.base_url = base_url
        self.auth = auth
        post_init = getattr(self, "__post_init__", None)
        if callable(post_init):
            post_init()

    async def request(self, method: str, path: str, *, params: dict[str, Any] | None = None, json: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError

    async def paginate(self, path: str, *, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        merged = dict(params or {})
        out: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            page_params = dict(merged)
            if cursor is not None:
                page_params["cursor"] = cursor
            payload = await self.request("GET", path, params=page_params)
            out.extend(payload.get("markets", []))
            cursor = payload.get("next_cursor")
            if not cursor:
                break
        return out
