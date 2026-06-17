from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db, AsyncSessionLocal
from app.core.security import get_current_user
from app.models.user import User
from app.models.track import Track
from app.schemas.track import TrackCreate, TrackResponse, TrackStatusResponse
from app.services.ai_music import start_music_generation, call_suno_api, VALID_AI_SERVICES

router = APIRouter(prefix="/music", tags=["music"])


def _ok(data: Any) -> dict:
    return {"success": True, "data": data, "error": None}


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_music(
    payload: TrackCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ai_service = (payload.ai_service or "suno").lower()
    if ai_service not in VALID_AI_SERVICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ai_service must be one of: {', '.join(sorted(VALID_AI_SERVICES))}",
        )

    track = Track(
        user_id=current_user.id,
        lyrics_id=payload.lyrics_id,
        title=payload.title,
        genre=payload.genre,
        bpm=payload.bpm,
        mood=payload.mood,
        status="processing",
        ai_service=ai_service,
    )
    db.add(track)
    await db.flush()
    await db.refresh(track)

    task_id = start_music_generation(str(track.id), background_tasks, AsyncSessionLocal)
    track.task_id = task_id
    await db.flush()

    return _ok(TrackResponse.model_validate(track).model_dump())


@router.get("")
async def list_tracks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Track)
        .where(Track.user_id == current_user.id)
        .order_by(desc(Track.created_at))
    )
    items = result.scalars().all()
    return _ok([TrackResponse.model_validate(item).model_dump() for item in items])


@router.get("/{track_id}/status")
async def get_track_status(
    track_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Track).where(Track.id == track_id, Track.user_id == current_user.id)
    )
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    return _ok(
        TrackStatusResponse(
            status=track.status,
            file_url=track.file_url,
            task_id=track.task_id,
            error_message=track.error_message,
        ).model_dump()
    )


@router.get("/{track_id}")
async def get_track(
    track_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Track).where(Track.id == track_id, Track.user_id == current_user.id)
    )
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    return _ok(TrackResponse.model_validate(track).model_dump())


@router.delete("/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_track(
    track_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Track).where(Track.id == track_id, Track.user_id == current_user.id)
    )
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    await db.delete(track)
