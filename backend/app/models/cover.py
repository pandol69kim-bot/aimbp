import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Cover(Base):
    __tablename__ = "covers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    album_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("albums.id", ondelete="SET NULL"), nullable=True
    )
    prompt_genre: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    prompt_mood: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    prompt_keywords: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    ai_model: Mapped[str] = mapped_column(String(50), nullable=False, default="gpt-image")
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    image_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    size: Mapped[str] = mapped_column(String(10), nullable=False, default="1:1")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
