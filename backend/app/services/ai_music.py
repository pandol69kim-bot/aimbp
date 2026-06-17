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

    # Try each service in order of reliability
    if ai_service == "mureka" and settings.has_mureka:
        logger.info(f"Using Mureka for track {track_id}")
        await _run_mureka_generation(track_id, db_session_factory, track)
    elif ai_service == "suno" and settings.has_suno:
        logger.info(f"Using Suno for track {track_id}")
        await _run_suno_generation(track_id, db_session_factory, track)
    else:
        logger.info(f"Using Mock MP3 for track {track_id}")
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


async def _run_suno_generation(track_id: str, db_session_factory, track) -> None:
    """Call Suno API, poll until done, then update the track. Fallback to mock on error."""
    try:
        suno_task_id = await _call_suno_generate(
            title=track.title,
            genre=track.genre or "",
            mood=track.mood or "",
        )

        file_url = None
        for attempt in range(120):  # poll up to 10 minutes (120 × 5s)
            await asyncio.sleep(5)
            result = await _poll_suno_task(suno_task_id)
            if result["status"] in ["completed", "success"]:
                file_url = result.get("audio_url") or result.get("file_url") or MOCK_MP3_URL
                break
            if result["status"] in ["failed", "error"]:
                logger.error(f"Suno task {suno_task_id} failed")
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
        error_msg = f"Suno API failed: {str(e)}"
        logger.error(f"Suno generation error for {track_id}: {error_msg}. Using mock MP3 instead.")

        # Save error message to database
        async with db_session_factory() as session:
            try:
                from app.models.track import Track
                db_result = await session.execute(select(Track).where(Track.id == uuid.UUID(track_id)))
                db_track = db_result.scalar_one_or_none()
                if db_track:
                    db_track.error_message = error_msg
                    await session.commit()
            except Exception:
                await session.rollback()

        await _mock_generation(track_id, db_session_factory)


async def _run_mureka_generation(track_id: str, db_session_factory, track) -> None:
    """Call Mureka API, poll until done, then update the track."""
    try:
        # Get lyrics if linked, otherwise use default
        lyrics_text = ""
        if track.lyrics_id:
            from app.models.lyrics import Lyrics
            async with db_session_factory() as session:
                result = await session.execute(
                    select(Lyrics).where(Lyrics.id == track.lyrics_id)
                )
                lyrics = result.scalar_one_or_none()
                if lyrics:
                    lyrics_text = f"{lyrics.verse}\n{lyrics.chorus}"

        # Fallback to default if no lyrics
        if not lyrics_text:
            lyrics_text = f"Verse 1\n{track.title} song\n\nChorus\nLet's enjoy {track.genre}"

        mureka_task_id = await _call_mureka_generate(
            title=track.title,
            genre=track.genre or "",
            mood=track.mood or "",
            lyrics=lyrics_text,
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
        error_msg = f"Mureka API failed: {str(e)}"
        logger.error(f"Mureka generation error for {track_id}: {error_msg}")
        async with db_session_factory() as session:
            try:
                from app.models.track import Track

                db_result = await session.execute(select(Track).where(Track.id == uuid.UUID(track_id)))
                db_track = db_result.scalar_one_or_none()
                if db_track:
                    db_track.status = "failed"
                    db_track.error_message = error_msg
                    await session.commit()
            except Exception:
                await session.rollback()


async def _call_mureka_generate(title: str, genre: str, mood: str, lyrics: str = "") -> str:
    """POST to Mureka /v1/song/generate. Returns mureka task id."""
    prompt_parts = [p for p in [genre, mood, title] if p]
    prompt = ", ".join(prompt_parts)

    logger.info(f"Calling Mureka API with prompt: {prompt}")

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(
                f"{settings.MUREKA_API_BASE}/v1/song/generate",
                headers={"Authorization": f"Bearer {settings.MUREKA_API_KEY}"},
                json={
                    "prompt": prompt,
                    "lyrics": lyrics,
                    "model": "auto",
                },
            )
            logger.info(f"Mureka API response: {resp.status_code}")
            resp.raise_for_status()
            data = resp.json()
            task_id = data.get("id")
            logger.info(f"Mureka task created: {task_id}")
            return task_id
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP {e.response.status_code}"
            try:
                error_json = e.response.json()
                if "error" in error_json:
                    error_detail = f"{error_detail}: {error_json['error'].get('message', 'Unknown error')}"
            except:
                error_detail = f"{error_detail}: {e.response.text[:200]}"
            logger.error(f"Mureka API error: {error_detail}")
            raise Exception(error_detail) from e


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


async def _call_suno_generate(title: str, genre: str, mood: str, lyrics: str = "") -> str:
    """POST to Suno API. Returns suno task id or mock ID on failure."""
    prompt_parts = [p for p in [genre, mood, title, lyrics] if p]
    prompt = ", ".join(prompt_parts)

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            # Try official Suno API endpoint
            resp = await client.post(
                f"{settings.SUNO_API_BASE}/api/generate",
                headers={"Authorization": f"Bearer {settings.SUNO_API_KEY}"},
                json={
                    "prompt": prompt,
                    "model": "chirp-v3-0606",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("id") or data.get("clip_id") or str(uuid.uuid4())
        except Exception as e:
            logger.warning(f"Suno API error: {e}. Using mock task_id.")
            return str(uuid.uuid4())


async def _poll_suno_task(task_id: str) -> dict:
    """GET to poll Suno task status. Returns status and audio_url when done."""
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"{settings.SUNO_API_BASE}/api/clips/{task_id}",
                headers={"Authorization": f"Bearer {settings.SUNO_API_KEY}"},
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "status": data.get("status", "processing"),
                "audio_url": data.get("audio_url") or data.get("file_url"),
            }
        except Exception as e:
            logger.warning(f"Suno poll error: {e}. Returning failed status.")
            return {"status": "failed", "audio_url": None}


async def call_suno_api(title: str, genre: str, mood: str, lyrics: str = "") -> dict:
    """Suno API call (real if key present, mock otherwise)."""
    if not settings.has_suno:
        logger.info("Suno API key not set; using mock response")
        return {"task_id": str(uuid.uuid4()), "status": "processing"}

    task_id = await _call_suno_generate(title=title, genre=genre, mood=mood, lyrics=lyrics)
    return {"task_id": task_id, "status": "processing"}


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
