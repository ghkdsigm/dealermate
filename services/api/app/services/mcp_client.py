from typing import Any

import httpx

from app.core.config import settings


class McpClient:
    def __init__(self) -> None:
        self.base_url = settings.mcp_orch_url.rstrip("/")

    async def call_tool(self, tool: str, args: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(f"{self.base_url}/tool/call", json={"tool": tool, "args": args})
            r.raise_for_status()
            return r.json()
