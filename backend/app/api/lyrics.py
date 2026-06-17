from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.lyrics import Lyrics
from app.schemas.lyrics import LyricsCreate, LyricsResponse
from app.services.ai_lyrics import generate_lyrics

router = APIRouter(prefix="/lyrics", tags=["lyrics"])


def _ok(data: Any) -> dict:
    return {"success": True, "data": data, "error": None}


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_lyrics_endpoint(
    payload: LyricsCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lyrics_data = await generate_lyrics(
        title=payload.title,
        prompt_subject=payload.prompt_subject,
        prompt_mood=payload.prompt_mood,
        prompt_genre=payload.prompt_genre,
        prompt_artist_style=payload.prompt_artist_style,
        prompt_language=payload.prompt_language,
        ai_model=payload.ai_model,
    )

    lyrics = Lyrics(
        user_id=current_user.id,
        title=payload.title,
        prompt_subject=payload.prompt_subject,
        prompt_mood=payload.prompt_mood,
        prompt_genre=payload.prompt_genre,
        prompt_artist_style=payload.prompt_artist_style,
        prompt_language=payload.prompt_language,
        ai_model=payload.ai_model,
        verse=lyrics_data["verse"],
        chorus=lyrics_data["chorus"],
        bridge=lyrics_data["bridge"],
        hook=lyrics_data["hook"],
    )
    db.add(lyrics)
    await db.flush()
    await db.refresh(lyrics)
    return _ok(LyricsResponse.model_validate(lyrics).model_dump())


@router.get("")
async def list_lyrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lyrics)
        .where(Lyrics.user_id == current_user.id)
        .order_by(desc(Lyrics.created_at))
    )
    items = result.scalars().all()
    return _ok([LyricsResponse.model_validate(item).model_dump() for item in items])


@router.get("/{lyrics_id}")
async def get_lyrics(
    lyrics_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lyrics).where(Lyrics.id == lyrics_id, Lyrics.user_id == current_user.id)
    )
    lyrics = result.scalar_one_or_none()
    if not lyrics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lyrics not found")
    return _ok(LyricsResponse.model_validate(lyrics).model_dump())


@router.delete("/{lyrics_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lyrics(
    lyrics_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lyrics).where(Lyrics.id == lyrics_id, Lyrics.user_id == current_user.id)
    )
    lyrics = result.scalar_one_or_none()
    if not lyrics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lyrics not found")
    await db.delete(lyrics)
