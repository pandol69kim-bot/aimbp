from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db, AsyncSessionLocal
from app.core.security import get_current_user
from app.models.user import User
from app.models.arrangement import Arrangement
from app.models.track import Track
from app.schemas.arrangement import ArrangementCreate, ArrangementResponse
from app.services.arrangement import start_arrangement_processing

router = APIRouter(prefix="/arrangement", tags=["arrangement"])


def _ok(data: Any) -> dict:
    return {"success": True, "data": data, "error": None}


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_arrangement(
    payload: ArrangementCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    track_result = await db.execute(
        select(Track).where(Track.id == payload.track_id, Track.user_id == current_user.id)
    )
    track = track_result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")

    arrangement = Arrangement(
        track_id=payload.track_id,
        user_id=current_user.id,
        instruments=payload.instruments,
        status="pending",
    )
    db.add(arrangement)
    await db.flush()
    await db.refresh(arrangement)

    start_arrangement_processing(str(arrangement.id), background_tasks, AsyncSessionLocal)

    return _ok(ArrangementResponse.model_validate(arrangement).model_dump())


@router.get("")
async def list_arrangements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Arrangement)
        .where(Arrangement.user_id == current_user.id)
        .order_by(desc(Arrangement.created_at))
    )
    items = result.scalars().all()
    return _ok([ArrangementResponse.model_validate(item).model_dump() for item in items])


@router.get("/{arrangement_id}")
async def get_arrangement(
    arrangement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Arrangement).where(
            Arrangement.id == arrangement_id,
            Arrangement.user_id == current_user.id,
        )
    )
    arrangement = result.scalar_one_or_none()
    if not arrangement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Arrangement not found"
        )
    return _ok(ArrangementResponse.model_validate(arrangement).model_dump())
