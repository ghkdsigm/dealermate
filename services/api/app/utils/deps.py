from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.utils.security import decode_token

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if cred is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        payload = decode_token(cred.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    employee_id = payload.get("sub")
    if not employee_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.employee_id == employee_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def require_role(*roles: str):
    def _inner(user: User = Depends(get_current_user)) -> User:
        if user.role.value not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return _inner
