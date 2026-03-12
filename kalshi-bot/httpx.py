from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib import request as urllib_request
from urllib.parse import urlencode
import json as json_lib


class HTTPStatusError(RuntimeError):
    pass


@dataclass
class Response:
    status_code: int
    content: bytes

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HTTPStatusError(f"HTTP request failed with status {self.status_code}")

    def json(self) -> dict[str, Any]:
        if not self.content:
            return {}
        return json_lib.loads(self.content.decode("utf-8"))


class AsyncClient:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    async def aclose(self) -> None:
        return None

    async def request(self, method: str, url: str, params=None, json=None, headers=None) -> Response:
        if params:
            q = urlencode(params)
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}{q}"
        body = None
        if json is not None:
            body = json_lib.dumps(json).encode("utf-8")
        req = urllib_request.Request(url, data=body, method=method.upper(), headers=headers or {})
        if body is not None and "Content-Type" not in req.headers:
            req.add_header("Content-Type", "application/json")
        with urllib_request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
            return Response(status_code=resp.status, content=resp.read())
