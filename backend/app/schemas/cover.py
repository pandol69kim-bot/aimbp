from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class CoverCreate(BaseModel):
    prompt_genre: str = Field(max_length=100, default="")
    prompt_mood: str = Field(max_length=100, default="")
    prompt_keywords: str = Field(max_length=500, default="")
    ai_model: str = Field(max_length=50, default="gpt-image")
    album_id: Optional[UUID] = None


class CoverResponse(BaseModel):
    id: UUID
    user_id: UUID
    album_id: Optional[UUID]
    prompt_genre: str
    prompt_mood: str
    prompt_keywords: str
    ai_model: str
    image_url: Optional[str]
    image_key: Optional[str]
    size: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
