from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class VocalLibraryResponse(BaseModel):
    id: UUID
    name: str
    gender: str
    genre: str
    sample_url: str
    is_active: bool
    description: Optional[str] = None
    elevenlabs_voice_id: Optional[str] = None

    model_config = {"from_attributes": True}


class VocalCreate(BaseModel):
    track_id: UUID
    library_id: UUID
    language: str = Field(default="korean", max_length=50)


class VocalResponse(BaseModel):
    id: UUID
    track_id: UUID
    user_id: UUID
    library_id: UUID
    language: str
    file_url: Optional[str]
    file_key: Optional[str]
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
