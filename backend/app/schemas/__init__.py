from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
)
from app.schemas.lyrics import LyricsCreate, LyricsResponse
from app.schemas.track import TrackCreate, TrackResponse, TrackStatusResponse
from app.schemas.album import AlbumCreate, AlbumUpdate, AlbumResponse, AddTrackRequest
from app.schemas.arrangement import ArrangementCreate, ArrangementResponse
from app.schemas.vocal import VocalLibraryResponse, VocalCreate, VocalResponse
from app.schemas.mastering import MasteringCreate, MasteringResponse
from app.schemas.cover import CoverCreate, CoverResponse

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "RefreshTokenRequest",
    "LyricsCreate",
    "LyricsResponse",
    "TrackCreate",
    "TrackResponse",
    "TrackStatusResponse",
    "AlbumCreate",
    "AlbumUpdate",
    "AlbumResponse",
    "AddTrackRequest",
    "ArrangementCreate",
    "ArrangementResponse",
    "VocalLibraryResponse",
    "VocalCreate",
    "VocalResponse",
    "MasteringCreate",
    "MasteringResponse",
    "CoverCreate",
    "CoverResponse",
]
