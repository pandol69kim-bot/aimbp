import base64
import logging
import os
import io
from typing import Any, List
from uuid import UUID
from datetime import datetime, timezone
from zipfile import ZipFile, ZIP_DEFLATED

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
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

    # 발행된 앨범은 수정 불가능
    if album.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Published albums cannot be modified"
        )

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

    # 발행된 앨범에는 음원 추가 불가능
    if album.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot add tracks to published albums"
        )

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

    # 발행된 앨범에서 음원 삭제 불가능
    if album.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove tracks from published albums"
        )

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


@router.post("/{album_id}/publish")
async def publish_album(
    album_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """앨범 발행 (수정 불가능하게 잠금)"""
    result = await db.execute(
        select(Album).where(Album.id == album_id, Album.user_id == current_user.id)
    )
    album = result.scalar_one_or_none()
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

    # 이미 발행된 경우
    if album.is_locked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Album is already published"
        )

    # 발행 전 검증
    album_tracks = await db.execute(
        select(AlbumTrack).where(AlbumTrack.album_id == album_id)
    )
    tracks = album_tracks.scalars().all()

    if not tracks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Album must have at least one track"
        )

    if not album.title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Album title is required"
        )

    if not album.cover_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Album cover is required"
        )

    # 발행 처리
    album.is_locked = True
    album.status = "published"
    album.published_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(album)
    await db.commit()

    return _ok({
        "message": "Album published successfully",
        "album": await _build_album_response(album, db)
    })


@router.get("/{album_id}/download")
async def download_album(
    album_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """발행된 앨범을 ZIP 파일로 다운로드"""
    result = await db.execute(
        select(Album).where(Album.id == album_id, Album.user_id == current_user.id)
    )
    album = result.scalar_one_or_none()
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

    # 발행된 앨범만 다운로드 가능
    if not album.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only published albums can be downloaded"
        )

    # 앨범 트랙 조회
    album_tracks_result = await db.execute(
        select(AlbumTrack)
        .where(AlbumTrack.album_id == album_id)
        .order_by(AlbumTrack.order)
    )
    album_tracks = album_tracks_result.scalars().all()

    # ZIP 파일 생성
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, 'w', ZIP_DEFLATED) as zip_file:
        # 커버 아트 추가
        if album.cover_url:
            try:
                # 원격 URL인 경우 간단히 참고만 하고, 로컬 파일인 경우 포함
                if album.cover_url.startswith("/app/uploads"):
                    with open(album.cover_url, 'rb') as f:
                        zip_file.writestr(f"{album.title}/cover.jpg", f.read())
            except Exception as e:
                logger.warning(f"Could not add cover to ZIP: {e}")

        # 음원 파일 추가
        for idx, album_track in enumerate(album_tracks, 1):
            track_result = await db.execute(
                select(Track).where(Track.id == album_track.track_id)
            )
            track = track_result.scalar_one_or_none()
            if track and track.file_url:
                try:
                    if track.file_url.startswith("/app/uploads"):
                        with open(track.file_url, 'rb') as f:
                            filename = f"{idx:02d}. {track.title}.mp3"
                            zip_file.writestr(f"{album.title}/audio/{filename}", f.read())
                except Exception as e:
                    logger.warning(f"Could not add track {track.title} to ZIP: {e}")

    zip_buffer.seek(0)

    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=album.zip"
        }
    )
