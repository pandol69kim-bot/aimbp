from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db, AsyncSessionLocal
from app.core.security import get_current_user
from app.models.user import User
from app.models.mastering import Mastering
from app.models.track import Track
from app.schemas.mastering import MasteringCreate, MasteringResponse
from app.services.mastering import start_mastering_processing

router = APIRouter(prefix="/mastering", tags=["mastering"])

VALID_PLATFORMS = {"spotify", "apple_music", "youtube", "soundcloud", "tidal"}


def _ok(data: Any) -> dict:
    return {"success": True, "data": data, "error": None}


@router.post("/process", status_code=status.HTTP_201_CREATED)
async def process_mastering(
    payload: MasteringCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.platform not in VALID_PLATFORMS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform must be one of: {', '.join(VALID_PLATFORMS)}",
        )

    track_result = await db.execute(
        select(Track).where(Track.id == payload.track_id, Track.user_id == current_user.id)
    )
    track = track_result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")

    input_url = payload.input_url or track.file_url or ""

    mastering = Mastering(
        track_id=payload.track_id,
        user_id=current_user.id,
        platform=payload.platform,
        input_url=input_url,
        status="pending",
    )
    db.add(mastering)
    await db.flush()
    await db.refresh(mastering)

    start_mastering_processing(str(mastering.id), background_tasks, AsyncSessionLocal)

    return _ok(MasteringResponse.model_validate(mastering).model_dump())


@router.get("")
async def list_masterings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Mastering)
        .where(Mastering.user_id == current_user.id)
        .order_by(desc(Mastering.created_at))
    )
    items = result.scalars().all()
    return _ok([MasteringResponse.model_validate(item).model_dump() for item in items])


@router.get("/{mastering_id}")
async def get_mastering(
    mastering_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Mastering).where(
            Mastering.id == mastering_id,
            Mastering.user_id == current_user.id,
        )
    )
    mastering = result.scalar_one_or_none()
    if not mastering:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mastering not found"
        )
    return _ok(MasteringResponse.model_validate(mastering).model_dump())
