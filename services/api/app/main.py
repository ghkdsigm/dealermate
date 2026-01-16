import logging

from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.user import Role, User
from app.routers import assist, auth, deals, health
from app.utils.security import hash_password

log = logging.getLogger("dealermate")


def seed_users(db: Session):
    # Demo accounts
    users = [
        {"employee_id": "D001", "name": "딜러 홍길동", "branch_id": "BR01", "role": Role.dealer, "password": "pass1234"},
        {"employee_id": "M001", "name": "상사 김관리", "branch_id": "BR01", "role": Role.manager, "password": "pass1234"},
        {"employee_id": "A001", "name": "관리자", "branch_id": "HQ", "role": Role.admin, "password": "pass1234"},
    ]
    for u in users:
        exists = db.query(User).filter(User.employee_id == u["employee_id"]).first()
        if exists:
            continue
        db.add(
            User(
                employee_id=u["employee_id"],
                name=u["name"],
                branch_id=u["branch_id"],
                role=u["role"],
                password_hash=hash_password(u["password"]),
            )
        )
    db.commit()


def create_app() -> FastAPI:
    app = FastAPI(title="DealerMate API", version="0.1.0")

    @app.on_event("startup")
    def on_startup():
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_users(db)
        finally:
            db.close()

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(deals.router)
    app.include_router(assist.router)

    return app


app = create_app()
