from pydantic import BaseModel, Field


class AssistRequest(BaseModel):
    deal_id: int | None = None
    message: str = Field(..., min_length=1)


class AssistResponse(BaseModel):
    intent: str
    used_tools: list[str] = []
    result: dict
