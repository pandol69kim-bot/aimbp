from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class AlbumCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None


class AlbumUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    cover_url: Optional[str] = None


class AddTrackRequest(BaseModel):
    track_id: UUID
    order: int = 0


class TrackInAlbum(BaseModel):
    album_track_id: UUID
    track_id: UUID
    order: int


class AlbumResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    cover_url: Optional[str]
    cover_key: Optional[str]
    status: str
    is_locked: bool = False
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    tracks: List[TrackInAlbum] = []

    model_config = {"from_attributes": True}
