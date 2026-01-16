import json
import os
from datetime import datetime
from typing import Any

import httpx
import redis
import structlog
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

log = structlog.get_logger("mcp-orchestrator")

INVENTORY_BASE_URL = os.getenv("INVENTORY_BASE_URL", "http://mcp-inventory:8000").rstrip("/")
HISTORY_BASE_URL = os.getenv("HISTORY_BASE_URL", "http://mcp-history:8000").rstrip("/")
PRICING_BASE_URL = os.getenv("PRICING_BASE_URL", "http://mcp-pricing:8000").rstrip("/")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

rds = redis.from_url(REDIS_URL, decode_responses=True)


class ToolCall(BaseModel):
    tool: str
    args: dict[str, Any] = {}


# Public registry (tool name -> remote endpoint)
TOOL_REGISTRY: dict[str, tuple[str, str]] = {
    # inventory
    "inventory.get_car_by_plate": (INVENTORY_BASE_URL, "/tools/get_car_by_plate"),
    "inventory.search_listings": (INVENTORY_BASE_URL, "/tools/search_listings"),
    "inventory.compare_listings": (INVENTORY_BASE_URL, "/tools/compare_listings"),
    # history
    "history.get_vehicle_registry_summary": (HISTORY_BASE_URL, "/tools/get_vehicle_registry_summary"),
    "history.get_maintenance_history": (HISTORY_BASE_URL, "/tools/get_maintenance_history"),
    # pricing
    "pricing.get_market_price": (PRICING_BASE_URL, "/tools/get_market_price"),
    # boss
    "boss.get_monthly_sales_stats": (INVENTORY_BASE_URL, "/tools/get_monthly_sales_stats"),
}


SENSITIVE_KEYS = {"phone", "email", "resident_no", "address", "kakao", "name"}


def mask_obj(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in SENSITIVE_KEYS:
                out[k] = "***"
            else:
                out[k] = mask_obj(v)
        return out
    if isinstance(obj, list):
        return [mask_obj(x) for x in obj]
    return obj


app = FastAPI(title="MCP Orchestrator", version="0.1.0")


@app.get("/health")
def health():
    return {"ok": True, "registry_size": len(TOOL_REGISTRY)}


@app.get("/tools")
def tools():
    return {
        "tools": [
            {"name": k, "upstream": v[0], "path": v[1]}
            for k, v in sorted(TOOL_REGISTRY.items(), key=lambda x: x[0])
        ]
    }


@app.post("/tool/call")
async def call_tool(payload: ToolCall):
    if payload.tool not in TOOL_REGISTRY:
        raise HTTPException(status_code=404, detail="Unknown tool")

    base, path = TOOL_REGISTRY[payload.tool]

    started = datetime.utcnow()
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(f"{base}{path}", json=payload.args)
            res.raise_for_status()
            data = res.json()
    except Exception as e:
        log.exception("tool_call_failed", tool=payload.tool)
        raise HTTPException(status_code=502, detail=f"Upstream error: {type(e).__name__}")

    masked = mask_obj(data)

    # audit log in redis stream
    event = {
        "tool": payload.tool,
        "args": json.dumps(mask_obj(payload.args), ensure_ascii=False),
        "result": json.dumps(masked, ensure_ascii=False)[:2000],
        "started_at": started.isoformat(),
        "finished_at": datetime.utcnow().isoformat(),
    }
    try:
        rds.xadd("mcp:audit", event, maxlen=5000, approximate=True)
    except Exception:
        pass

    return masked
