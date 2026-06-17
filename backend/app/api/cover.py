from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db, AsyncSessionLocal
from app.core.security import get_current_user
from app.models.user import User
from app.models.cover import Cover
from app.schemas.cover import CoverCreate, CoverResponse
from app.services.cover import start_cover_processing

router = APIRouter(prefix="/cover", tags=["cover"])

COVER_SIZES = ["1:1", "16:9", "9:16"]


def _ok(data: Any) -> dict:
    return {"success": True, "data": data, "error": None}


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_covers(
    payload: CoverCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate 3 cover images (1:1, 16:9, 9:16) simultaneously."""
    covers = []

    for size in COVER_SIZES:
        cover = Cover(
            user_id=current_user.id,
            album_id=payload.album_id,
            prompt_genre=payload.prompt_genre,
            prompt_mood=payload.prompt_mood,
            prompt_keywords=payload.prompt_keywords,
            ai_model=payload.ai_model,
            size=size,
            status="pending",
        )
        db.add(cover)
        covers.append(cover)

    await db.flush()
    for cover in covers:
        await db.refresh(cover)

    for cover in covers:
        start_cover_processing(str(cover.id), background_tasks, AsyncSessionLocal)

    return _ok([CoverResponse.model_validate(c).model_dump() for c in covers])


@router.get("")
async def list_covers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Cover)
        .where(Cover.user_id == current_user.id)
        .order_by(desc(Cover.created_at))
    )
    items = result.scalars().all()
    return _ok([CoverResponse.model_validate(item).model_dump() for item in items])


@router.get("/{cover_id}")
async def get_cover(
    cover_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Cover).where(Cover.id == cover_id, Cover.user_id == current_user.id)
    )
    cover = result.scalar_one_or_none()
    if not cover:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cover not found")
    return _ok(CoverResponse.model_validate(cover).model_dump())
