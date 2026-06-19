from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class TrackCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    genre: str = Field(max_length=100, default="")
    bpm: Optional[int] = None
    mood: Optional[str] = Field(default=None, max_length=100)
    lyrics_id: Optional[UUID] = None
    ai_service: Optional[str] = Field(default="suno", max_length=50)


class TrackResponse(BaseModel):
    id: UUID
    user_id: UUID
    lyrics_id: Optional[UUID]
    title: str
    artist_name: Optional[str] = None
    genre: str
    bpm: Optional[int]
    mood: Optional[str]
    file_url: Optional[str]
    file_key: Optional[str]
    status: str
    duration: Optional[float]
    ai_service: Optional[str]
    task_id: Optional[str]
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TrackStatusResponse(BaseModel):
    status: str
    file_url: Optional[str] = None
    task_id: Optional[str] = None
    error_message: Optional[str] = None
