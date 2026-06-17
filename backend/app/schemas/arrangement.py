from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class ArrangementCreate(BaseModel):
    track_id: UUID
    instruments: List[str] = Field(default_factory=list)


class ArrangementResponse(BaseModel):
    id: UUID
    track_id: UUID
    user_id: UUID
    instruments: List[str]
    wav_url: Optional[str]
    mp3_url: Optional[str]
    stems: Optional[Dict[str, Any]]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
