from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class LyricsCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    prompt_subject: str = Field(max_length=500, default="")
    prompt_mood: str = Field(max_length=100, default="")
    prompt_genre: str = Field(max_length=100, default="")
    prompt_artist_style: str = Field(max_length=255, default="")
    prompt_language: str = Field(max_length=50, default="korean")
    ai_model: str = Field(max_length=50, default="openai")


class LyricsResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    prompt_subject: str
    prompt_mood: str
    prompt_genre: str
    prompt_artist_style: str
    prompt_language: str
    ai_model: str
    verse: str
    chorus: str
    bridge: str
    hook: str
    created_at: datetime

    model_config = {"from_attributes": True}
