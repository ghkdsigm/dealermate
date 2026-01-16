from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.quick_question import QuickQuestion
from app.utils.deps import get_current_user


router = APIRouter(prefix="/quick-questions", tags=["quick-questions"])


class QuickQuestionCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=240)


@router.get("")
def list_quick_questions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    items = (
        db.query(QuickQuestion)
        .filter(QuickQuestion.owner_user_id == user.id)
        .order_by(QuickQuestion.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": q.id,
            "text": q.text,
            "created_at": q.created_at.isoformat(),
        }
        for q in items
    ]


@router.post("")
def create_quick_question(payload: QuickQuestionCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = QuickQuestion(owner_user_id=user.id, text=payload.text.strip())
    db.add(q)
    db.commit()
    db.refresh(q)
    return {"id": q.id, "text": q.text, "created_at": q.created_at.isoformat()}


@router.delete("/{qid}")
def delete_quick_question(qid: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(QuickQuestion).filter(QuickQuestion.id == qid, QuickQuestion.owner_user_id == user.id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(q)
    db.commit()
    return {"ok": True}
