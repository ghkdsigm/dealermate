from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.mcp_client import McpClient
from app.utils.deps import get_current_user


router = APIRouter(prefix="/filters", tags=["filters"])


class FilterSearchRequest(BaseModel):
    query: str | None = None
    filters: dict[str, Any] = {}
    top_k: int = 50


mcp = McpClient()


@router.get("/options")
async def get_filter_options(db: Session = Depends(get_db), user=Depends(get_current_user)):
    res = await mcp.call_tool(
        "inventory.get_filter_options",
        {"branch_id": user.branch_id, "dealer_employee_id": user.employee_id},
    )
    return res


@router.post("/search")
async def search_with_filters(payload: FilterSearchRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    args = {
        "query": payload.query or "",
        "top_k": max(1, min(payload.top_k, 200)),
        "branch_id": user.branch_id,
        "dealer_employee_id": user.employee_id,
        "filters": payload.filters or {},
    }
    res = await mcp.call_tool("inventory.search_listings_filtered", args)
    return res
