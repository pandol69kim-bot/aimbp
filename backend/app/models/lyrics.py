import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Lyrics(Base):
    __tablename__ = "lyrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt_subject: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    prompt_mood: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    prompt_genre: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    prompt_artist_style: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    prompt_language: Mapped[str] = mapped_column(String(50), nullable=False, default="korean")
    ai_model: Mapped[str] = mapped_column(String(50), nullable=False, default="openai")
    verse: Mapped[str] = mapped_column(Text, nullable=False, default="")
    chorus: Mapped[str] = mapped_column(Text, nullable=False, default="")
    bridge: Mapped[str] = mapped_column(Text, nullable=False, default="")
    hook: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
