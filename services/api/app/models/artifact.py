import enum
from datetime import datetime

from sqlalchemy import String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ArtifactType(str, enum.Enum):
    briefing = "briefing"
    compare_sheet = "compare_sheet"
    follow_up = "follow_up"
    script = "script"


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deals.id"), index=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[ArtifactType] = mapped_column(Enum(ArtifactType))
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
