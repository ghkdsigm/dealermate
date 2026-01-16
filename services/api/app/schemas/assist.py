from pydantic import BaseModel, Field
from typing import Any


class AssistRequest(BaseModel):
    deal_id: int | None = None
    message: str = Field(..., min_length=1)
    filters: dict[str, Any] | None = None


class AssistResponse(BaseModel):
    intent: str
    used_tools: list[str] = []
    result: dict
