import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db, AsyncSessionLocal
from app.core.security import get_current_user
from app.models.user import User
from app.models.track import Track
from app.schemas.track import TrackCreate, TrackResponse, TrackStatusResponse
from app.services.ai_music import start_music_generation, call_suno_api, VALID_AI_SERVICES, MOCK_MP3_URL

logger = logging.getLogger(__name__)

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


@router.post("/webhook/suno")
async def suno_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Receive callback from sunoapi.org when music generation completes.

    sunoapi.org callback structure:
    {
      "code": 200,
      "msg": "...",
      "data": {
        "task_id": "...",
        "callbackType": "text" | "audio" | "first_audio",
        "data": [
          {
            "id": "...",
            "audio_url": "...",           # empty on text callback
            "stream_audio_url": "...",    # streaming audio URL
            "source_stream_audio_url": "...",
            "image_url": "...",
            "title": "...",
            "tags": "...",
          }
        ]
      }
    }
    """
    body = await request.json()
    logger.info(f"Suno webhook received: {body}")

    # task_id is nested inside data
    outer_data = body.get("data", {})
    task_id = outer_data.get("task_id") if isinstance(outer_data, dict) else None
    callback_type = outer_data.get("callbackType", "") if isinstance(outer_data, dict) else ""

    if not task_id:
        logger.warning(f"Suno webhook: no task_id in payload. body keys={list(body.keys())}")
        return {"success": False, "error": "No task_id"}

    result = await db.execute(select(Track).where(Track.task_id == task_id))
    track = result.scalar_one_or_none()
    if not track:
        logger.warning(f"Suno webhook: track not found for task_id={task_id}")
        return {"success": True}  # 200 반환하여 재전송 방지

    clips = outer_data.get("data", []) if isinstance(outer_data, dict) else []
    audio_url = None
    if clips and isinstance(clips, list):
        clip = clips[0]
        # audio_url이 비어있으면 stream_audio_url 사용
        audio_url = (
            clip.get("audio_url")
            or clip.get("stream_audio_url")
            or clip.get("source_stream_audio_url")
        ) or None

    code = body.get("code")
    is_success = str(code) == "200" or code == 200

    if callback_type in ("audio", "first_audio") and audio_url:
        track.status = "completed"
        track.file_url = audio_url
        track.duration = 180.0
        logger.info(f"Track {track.id} completed (audio). url={audio_url}")
    elif callback_type == "text" and is_success:
        # 텍스트(가사) 생성 완료 — 오디오 콜백을 추가로 기다림
        # stream_audio_url이 있으면 임시로 사용 (실제 오디오 URL로 업데이트됨)
        if audio_url:
            track.status = "completed"
            track.file_url = audio_url
            track.duration = 180.0
            logger.info(f"Track {track.id} completed (text+stream). url={audio_url}")
        else:
            logger.info(f"Track {track.id} text generated, waiting for audio callback.")
    elif not is_success:
        track.status = "failed"
        track.error_message = body.get("msg") or "Generation failed"
        logger.warning(f"Track {track.id} failed: {track.error_message}")

    await db.commit()
    return {"success": True}


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
