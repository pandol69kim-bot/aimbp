import asyncio
import logging
import uuid

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings

logger = logging.getLogger(__name__)

MOCK_MP3_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

VALID_AI_SERVICES = {"suno", "mureka", "udio"}


async def _simulate_music_generation(track_id: str, db_session_factory) -> None:
    """Background task: real API call if key present, otherwise mock with 5s delay."""
    from app.models.track import Track

    async with db_session_factory() as session:
        result = await session.execute(select(Track).where(Track.id == uuid.UUID(track_id)))
        track = result.scalar_one_or_none()
        if not track:
            return

    ai_service = track.ai_service or "suno"

    if ai_service == "mureka" and settings.has_mureka:
        await _run_mureka_generation(track_id, db_session_factory, track)
    else:
        await _mock_generation(track_id, db_session_factory)


async def _mock_generation(track_id: str, db_session_factory) -> None:
    await asyncio.sleep(5)
    async with db_session_factory() as session:
        try:
            from app.models.track import Track

            result = await session.execute(select(Track).where(Track.id == uuid.UUID(track_id)))
            track = result.scalar_one_or_none()
            if track:
                track.status = "completed"
                track.file_url = MOCK_MP3_URL
                track.duration = 180.0
                await session.commit()
                logger.info(f"Mock generation completed for track {track_id}")
        except Exception as e:
            logger.error(f"Mock generation error for {track_id}: {e}")
            await session.rollback()


async def _run_mureka_generation(track_id: str, db_session_factory, track) -> None:
    """Call Mureka API, poll until done, then update the track."""
    try:
        mureka_task_id = await _call_mureka_generate(
            title=track.title,
            genre=track.genre or "",
            mood=track.mood or "",
        )

        file_url = None
        for attempt in range(24):  # poll up to 2 minutes (24 × 5s)
            await asyncio.sleep(5)
            result = await _poll_mureka_task(mureka_task_id)
            if result["status"] == "completed":
                file_url = result.get("audio_url") or MOCK_MP3_URL
                break
            if result["status"] == "failed":
                logger.error(f"Mureka task {mureka_task_id} failed")
                break

        async with db_session_factory() as session:
            from app.models.track import Track

            db_result = await session.execute(select(Track).where(Track.id == uuid.UUID(track_id)))
            db_track = db_result.scalar_one_or_none()
            if db_track:
                db_track.status = "completed" if file_url else "failed"
                db_track.file_url = file_url
                db_track.duration = 180.0
                await session.commit()

    except Exception as e:
        logger.error(f"Mureka generation error for {track_id}: {e}")
        async with db_session_factory() as session:
            try:
                from app.models.track import Track

                db_result = await session.execute(select(Track).where(Track.id == uuid.UUID(track_id)))
                db_track = db_result.scalar_one_or_none()
                if db_track:
                    db_track.status = "failed"
                    await session.commit()
            except Exception:
                await session.rollback()


async def _call_mureka_generate(title: str, genre: str, mood: str, lyrics: str = "") -> str:
    """POST to Mureka /v1/song/generate. Returns mureka task id."""
    prompt_parts = [p for p in [genre, mood, title] if p]
    prompt = ", ".join(prompt_parts)

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.MUREKA_API_BASE}/v1/song/generate",
            headers={"Authorization": f"Bearer {settings.MUREKA_API_KEY}"},
            json={
                "prompt": prompt,
                "lyrics": lyrics,
                "model": "auto",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["id"]


async def _poll_mureka_task(task_id: str) -> dict:
    """GET /v1/song/{task_id} — returns status and audio_url when done."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{settings.MUREKA_API_BASE}/v1/song/{task_id}",
            headers={"Authorization": f"Bearer {settings.MUREKA_API_KEY}"},
        )
        resp.raise_for_status()
        data = resp.json()
        # Normalise response shape: {status, audio_url}
        return {
            "status": data.get("status", "processing"),
            "audio_url": data.get("audio_url") or data.get("url"),
        }


def start_music_generation(track_id: str, background_tasks, db_session_factory) -> str:
    task_id = str(uuid.uuid4())
    background_tasks.add_task(_simulate_music_generation, track_id, db_session_factory)
    return task_id


async def call_suno_api(title: str, genre: str, mood: str, lyrics: str = "") -> dict:
    """Mock Suno API call."""
    if not settings.SUNO_API_KEY or settings.SUNO_API_KEY == "your-suno-api-key":
        logger.info("Suno API key not set; using mock response")
        return {"task_id": str(uuid.uuid4()), "status": "processing"}
    return {"task_id": str(uuid.uuid4()), "status": "processing"}


async def call_mureka_api(title: str, genre: str, mood: str, lyrics: str = "") -> dict:
    """Mureka API call (real if key present, mock otherwise)."""
    if not settings.has_mureka:
        logger.info("Mureka API key not set; using mock response")
        return {"task_id": str(uuid.uuid4()), "status": "processing"}

    task_id = await _call_mureka_generate(title=title, genre=genre, mood=mood, lyrics=lyrics)
    return {"task_id": task_id, "status": "processing"}


async def poll_music_status(task_id: str, ai_service: str = "suno") -> dict:
    if ai_service == "mureka" and settings.has_mureka:
        return await _poll_mureka_task(task_id)
    return {"status": "completed", "file_url": MOCK_MP3_URL, "duration": 180.0}
