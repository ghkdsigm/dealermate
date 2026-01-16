import enum
from datetime import datetime

from sqlalchemy import String, DateTime, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Role(str, enum.Enum):
    dealer = "dealer"
    manager = "manager"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    branch_id: Mapped[str] = mapped_column(String(64), index=True)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.dealer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow)
