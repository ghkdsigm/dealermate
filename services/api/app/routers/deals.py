import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.deal import Deal
from app.utils.deps import get_current_user

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("")
def list_deals(db: Session = Depends(get_db), user=Depends(get_current_user)):
    qs = db.query(Deal).filter(Deal.owner_user_id == user.id).order_by(Deal.updated_at.desc()).limit(50).all()
    return [
        {
            "id": d.id,
            "customer_token": d.customer_token,
            "status": d.status.value,
            "preference": json.loads(d.preference_json or "{}"),
            "updated_at": d.updated_at.isoformat(),
        }
        for d in qs
    ]
