from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class MasteringCreate(BaseModel):
    track_id: UUID
    platform: str = Field(max_length=50)
    input_url: Optional[str] = Field(default=None, max_length=1024)


class MasteringResponse(BaseModel):
    id: UUID
    track_id: UUID
    user_id: UUID
    platform: str
    input_url: Optional[str]
    output_url: Optional[str]
    output_key: Optional[str]
    lufs: Optional[float]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
