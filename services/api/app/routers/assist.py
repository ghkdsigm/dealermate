from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.assist import AssistRequest, AssistResponse
from app.services.assistant_service import AssistantService
from app.utils.deps import get_current_user

router = APIRouter(prefix="/assistant", tags=["assistant"])

svc = AssistantService()


@router.post("/assist", response_model=AssistResponse)
async def assist(payload: AssistRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    res = await svc.assist(db=db, user=user, message=payload.message, deal_id=payload.deal_id)
    return AssistResponse(**res)
