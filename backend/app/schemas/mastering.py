from pydantic import BaseModel, Field, model_validator
from typing import Optional, Any
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
    original_url: Optional[str] = None
    mastered_url: Optional[str] = None
    lufs: Optional[float] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode='before')
    @classmethod
    def map_url_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data.setdefault('original_url', data.get('input_url'))
            data.setdefault('mastered_url', data.get('output_url'))
            return data
        # ORM 객체
        return {
            'id': data.id,
            'track_id': data.track_id,
            'user_id': data.user_id,
            'platform': data.platform,
            'original_url': getattr(data, 'input_url', None),
            'mastered_url': getattr(data, 'output_url', None),
            'lufs': getattr(data, 'lufs', None),
            'status': data.status,
            'created_at': data.created_at,
        }
