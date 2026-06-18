import base64
import logging
import os
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.album import Album, AlbumTrack
from app.models.cover import Cover
from app.models.track import Track
from app.schemas.album import AlbumCreate, AlbumUpdate, AlbumResponse, AddTrackRequest, TrackInAlbum

logger = logging.getLogger(__name__)


class ApplyCoverRequest(BaseModel):
    cover_id: str

router = APIRouter(prefix="/albums", tags=["albums"])


def _ok(data: Any) -> dict:
    return {"success": True, "data": data, "error": None}


async def _build_album_response(album: Album, db: AsyncSession) -> dict:
    result = await db.execute(
        select(AlbumTrack).where(AlbumTrack.album_id == album.id).order_by(AlbumTrack.order)
    )
    album_tracks = result.scalars().all()

    resp = AlbumResponse.model_validate(album)
    data = resp.model_dump()
    data["tracks"] = [
        TrackInAlbum(album_track_id=at.id, track_id=at.track_id, order=at.order).model_dump()
        for at in album_tracks
    ]
    return data


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_album(
    payload: AlbumCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    album = Album(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
    )
    db.add(album)
    await db.flush()
    await db.refresh(album)
    return _ok(await _build_album_response(album, db))


@router.get("")
async def list_albums(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Album)
        .where(Album.user_id == current_user.id)
        .order_by(desc(Album.created_at))
    )
    albums = result.scalars().all()
    responses = [await _build_album_response(a, db) for a in albums]
    return _ok(responses)


@router.get("/{album_id}")
async def get_album(
    album_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Album).where(Album.id == album_id, Album.user_id == current_user.id)
    )
    album = result.scalar_one_or_none()
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")
    return _ok(await _build_album_response(album, db))


@router.patch("/{album_id}")
async def update_album(
    album_id: UUID,
    payload: AlbumUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Album).where(Album.id == album_id, Album.user_id == current_user.id)
    )
    album = result.scalar_one_or_none()
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

    if payload.title is not None:
        album.title = payload.title
    if payload.description is not None:
        album.description = payload.description
    if payload.status is not None:
        album.status = payload.status
    if payload.cover_url is not None:
        album.cover_url = payload.cover_url

    await db.flush()
    await db.refresh(album)
    return _ok(await _build_album_response(album, db))


@router.post("/{album_id}/cover")
async def apply_cover_to_album(
    album_id: UUID,
    payload: ApplyCoverRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Album).where(Album.id == album_id, Album.user_id == current_user.id)
    )
    album = result.scalar_one_or_none()
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

    cover_result = await db.execute(
        select(Cover).where(Cover.id == UUID(payload.cover_id), Cover.user_id == current_user.id)
    )
    cover = cover_result.scalar_one_or_none()
    if not cover:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cover not found")

    image_url = cover.image_url
    if image_url and image_url.startswith("data:image/"):
        try:
            _, b64_data = image_url.split(",", 1)
            img_bytes = base64.b64decode(b64_data)
            covers_dir = "/app/uploads/covers"
            os.makedirs(covers_dir, exist_ok=True)
            size_key = cover.size.replace(":", "x")
            filename = f"cover_{cover.id}_{size_key}.png"
            with open(f"{covers_dir}/{filename}", "wb") as f:
                f.write(img_bytes)
            image_url = f"{settings.FILE_BASE_URL}/api/v1/files/local/covers/{filename}"
            cover.image_url = image_url
            await db.flush()
            logger.info(f"Saved cover {cover.id} to file: {filename}")
        except Exception as e:
            logger.warning(f"Failed to save cover image file: {e}")

    album.cover_url = image_url
    await db.flush()
    await db.refresh(album)
    return _ok(await _build_album_response(album, db))


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album(
    album_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Album).where(Album.id == album_id, Album.user_id == current_user.id)
    )
    album = result.scalar_one_or_none()
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")
    await db.delete(album)


@router.post("/{album_id}/tracks", status_code=status.HTTP_201_CREATED)
async def add_track_to_album(
    album_id: UUID,
    payload: AddTrackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Album).where(Album.id == album_id, Album.user_id == current_user.id)
    )
    album = result.scalar_one_or_none()
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

    track_result = await db.execute(
        select(Track).where(Track.id == payload.track_id, Track.user_id == current_user.id)
    )
    track = track_result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")

    existing = await db.execute(
        select(AlbumTrack).where(
            AlbumTrack.album_id == album_id,
            AlbumTrack.track_id == payload.track_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Track already in album",
        )

    album_track = AlbumTrack(
        album_id=album_id,
        track_id=payload.track_id,
        order=payload.order,
    )
    db.add(album_track)
    await db.flush()
    return _ok(await _build_album_response(album, db))


@router.delete("/{album_id}/tracks/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_track_from_album(
    album_id: UUID,
    track_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Album).where(Album.id == album_id, Album.user_id == current_user.id)
    )
    album = result.scalar_one_or_none()
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

    at_result = await db.execute(
        select(AlbumTrack).where(
            AlbumTrack.album_id == album_id,
            AlbumTrack.track_id == track_id,
        )
    )
    album_track = at_result.scalar_one_or_none()
    if not album_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found in album",
        )
    await db.delete(album_track)
