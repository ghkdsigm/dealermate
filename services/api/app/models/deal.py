import enum
from datetime import datetime

from sqlalchemy import String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DealStatus(str, enum.Enum):
    new = "new"
    qualifying = "qualifying"
    recommending = "recommending"
    negotiating = "negotiating"
    follow_up = "follow_up"
    contracted = "contracted"
    lost = "lost"


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    customer_token: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[DealStatus] = mapped_column(Enum(DealStatus), default=DealStatus.new)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    preference_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow)
