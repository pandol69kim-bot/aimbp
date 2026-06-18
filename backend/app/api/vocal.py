from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db, AsyncSessionLocal
from app.core.security import get_current_user
from app.models.user import User
from app.models.vocal import VocalLibrary, Vocal
from app.models.track import Track
from app.schemas.vocal import VocalLibraryResponse, VocalCreate, VocalResponse
from app.services.vocal import start_vocal_processing, SAMPLE_VOCAL_LIBRARY

router = APIRouter(prefix="/vocal", tags=["vocal"])


def _ok(data: Any) -> dict:
    return {"success": True, "data": data, "error": None}


@router.get("/library")
async def get_vocal_library(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VocalLibrary).where(VocalLibrary.is_active == True)
    )
    items = result.scalars().all()

    if not items:
        for entry in SAMPLE_VOCAL_LIBRARY:
            db.add(VocalLibrary(**entry))
        await db.commit()
        result = await db.execute(
            select(VocalLibrary).where(VocalLibrary.is_active == True)
        )
        items = result.scalars().all()

    return _ok([VocalLibraryResponse.model_validate(item).model_dump() for item in items])


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_vocal(
    payload: VocalCreate,
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

    library_result = await db.execute(
        select(VocalLibrary).where(
            VocalLibrary.id == payload.library_id,
            VocalLibrary.is_active == True,
        )
    )
    library = library_result.scalar_one_or_none()
    if not library:
        # Accept mock IDs from SAMPLE_VOCAL_LIBRARY
        mock_ids = [str(v["id"]) for v in SAMPLE_VOCAL_LIBRARY]
        if str(payload.library_id) not in mock_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vocal library entry not found"
            )

    vocal = Vocal(
        track_id=payload.track_id,
        user_id=current_user.id,
        library_id=payload.library_id,
        language=payload.language,
        status="pending",
    )
    db.add(vocal)
    await db.flush()
    await db.refresh(vocal)

    start_vocal_processing(str(vocal.id), background_tasks, AsyncSessionLocal)

    return _ok(VocalResponse.model_validate(vocal).model_dump())


@router.get("")
async def list_vocals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vocal)
        .where(Vocal.user_id == current_user.id)
        .order_by(desc(Vocal.created_at))
    )
    items = result.scalars().all()
    return _ok([VocalResponse.model_validate(item).model_dump() for item in items])


@router.get("/{vocal_id}")
async def get_vocal(
    vocal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vocal).where(Vocal.id == vocal_id, Vocal.user_id == current_user.id)
    )
    vocal = result.scalar_one_or_none()
    if not vocal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vocal not found")
    return _ok(VocalResponse.model_validate(vocal).model_dump())
