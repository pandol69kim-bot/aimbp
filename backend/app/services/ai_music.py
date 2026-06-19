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
    """Background task: select generation mode based on config."""
    from app.models.track import Track

    async with db_session_factory() as session:
        result = await session.execute(select(Track).where(Track.id == uuid.UUID(track_id)))
        track = result.scalar_one_or_none()
        if not track:
            return

    ai_service = track.ai_service or "suno"
    mode = settings.MUSIC_GENERATION_MODE.lower()

    # Determine which generation method to use
    if mode == "mock":
        logger.info(f"Using MOCK generation for track {track_id} (mode=mock)")
        await _mock_generation(track_id, db_session_factory)
    elif mode == "real":
        logger.info(f"Using REAL API for track {track_id} (mode=real)")
        if ai_service == "mureka":
            await _run_mureka_generation(track_id, db_session_factory, track)
        elif ai_service == "suno":
            await _run_suno_generation(track_id, db_session_factory, track)
        else:
            await _mock_generation(track_id, db_session_factory)
    else:  # auto mode
        if ai_service == "mureka" and settings.has_mureka:
            logger.info(f"Using Mureka for track {track_id} (auto mode)")
            await _run_mureka_generation(track_id, db_session_factory, track)
        elif ai_service == "suno" and settings.has_suno:
            logger.info(f"Using Suno for track {track_id} (auto mode)")
            await _run_suno_generation(track_id, db_session_factory, track)
        else:
            logger.info(f"Using MOCK generation for track {track_id} (auto mode, no API key)")
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
    """Submit request to sunoapi.org and poll for completion. No webhook needed."""
    try:
        suno_task_id = await _call_suno_generate(
            title=track.title,
            genre=track.genre or "",
            mood=track.mood or "",
            track_id=track_id,
        )

        async with db_session_factory() as session:
            from app.models.track import Track

            db_result = await session.execute(select(Track).where(Track.id == uuid.UUID(track_id)))
            db_track = db_result.scalar_one_or_none()
            if db_track:
                db_track.task_id = suno_task_id
                await session.commit()
                logger.info(f"Suno task submitted: taskId={suno_task_id}, track={track_id}")

        # Start polling for completion (max 10 minutes, poll every 10 seconds)
        await _poll_suno_generation(track_id, suno_task_id, db_session_factory)

    except Exception as e:
        error_msg = f"Suno API failed: {str(e)}"
        logger.error(f"Suno generation error for {track_id}: {error_msg}")

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


async def _poll_suno_generation(track_id: str, suno_task_id: str, db_session_factory) -> None:
    """Poll Suno API for completion. Max 60 attempts × 10s = 10 minutes."""
    from app.models.track import Track

    for attempt in range(60):
        await asyncio.sleep(10)  # Poll every 10 seconds

        try:
            result = await _poll_suno_task(suno_task_id)

            if result["status"] == "completed":
                # Task completed successfully
                async with db_session_factory() as session:
                    db_result = await session.execute(select(Track).where(Track.id == uuid.UUID(track_id)))
                    db_track = db_result.scalar_one_or_none()
                    if db_track:
                        db_track.status = "completed"
                        db_track.file_url = result.get("audio_url", MOCK_MP3_URL)
                        db_track.duration = 180.0
                        await session.commit()
                        logger.info(f"Suno task {suno_task_id} completed for track {track_id}")
                return

            elif result["status"] == "failed":
                # Task failed
                async with db_session_factory() as session:
                    db_result = await session.execute(select(Track).where(Track.id == uuid.UUID(track_id)))
                    db_track = db_result.scalar_one_or_none()
                    if db_track:
                        db_track.status = "failed"
                        db_track.error_message = result.get("error", "Suno generation failed")
                        await session.commit()
                        logger.error(f"Suno task {suno_task_id} failed for track {track_id}")
                return

            logger.info(f"Suno task {suno_task_id} still processing (attempt {attempt+1}/60)")

        except Exception as e:
            logger.error(f"Error polling Suno task {suno_task_id}: {e}")
            # Continue polling even if there's an error

    # Timeout: max polling duration exceeded
    async with db_session_factory() as session:
        db_result = await session.execute(select(Track).where(Track.id == uuid.UUID(track_id)))
        db_track = db_result.scalar_one_or_none()
        if db_track:
            db_track.status = "failed"
            db_track.error_message = "Suno generation timeout (10 minutes exceeded)"
            await session.commit()
            logger.error(f"Suno task {suno_task_id} timeout for track {track_id}")


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


async def _call_suno_generate(title: str, genre: str, mood: str, lyrics: str = "", track_id: str = "") -> str:
    """POST to sunoapi.org /api/v1/generate. Returns task ID. No webhook needed - we poll for status."""
    tags = ", ".join(p for p in [genre, mood] if p)

    # customMode=True when lyrics provided, else description mode
    if lyrics:
        payload = {
            "prompt": lyrics,
            "model": "V4",
            "customMode": True,
            "title": title,
            "tags": tags,
            "instrumental": False,
        }
    else:
        prompt = ", ".join(p for p in [genre, mood, title] if p)
        payload = {
            "prompt": prompt,
            "model": "V4",
            "customMode": False,
            "instrumental": False,
        }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(
                f"{settings.SUNO_API_BASE}/api/v1/generate",
                headers={"Authorization": f"Bearer {settings.SUNO_API_KEY}"},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != 200:
                raise Exception(data.get("msg", "Unknown error from sunoapi.org"))
            task_id = data.get("data", {}).get("taskId")
            if not task_id:
                raise Exception(f"No taskId in response: {data}")
            logger.info(f"Suno task created: taskId={task_id}")
            return task_id
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP {e.response.status_code}"
            try:
                error_json = e.response.json()
                error_detail = f"{error_detail}: {error_json.get('msg', e.response.text[:200])}"
            except Exception:
                error_detail = f"{error_detail}: {e.response.text[:200]}"
            logger.error(f"Suno API error: {error_detail}")
            raise Exception(error_detail) from e
        except Exception as e:
            logger.error(f"Suno API error: {str(e)}")
            raise


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


async def _poll_suno_task(task_id: str) -> dict:
    """Query Suno API for task status. Returns {status, audio_url, error}."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            # Try fetching with task ID in query params
            resp = await client.get(
                f"{settings.SUNO_API_BASE}/api/v1/query",
                headers={"Authorization": f"Bearer {settings.SUNO_API_KEY}"},
                params={"task_ids": task_id},
            )

            if resp.status_code == 404:
                # Try alternative endpoint
                resp = await client.get(
                    f"{settings.SUNO_API_BASE}/api/v1/fetch",
                    headers={"Authorization": f"Bearer {settings.SUNO_API_KEY}"},
                    params={"task_id": task_id},
                )

            resp.raise_for_status()
            data = resp.json()

            if data.get("code") == 200:
                # Expected response format from sunoapi.org
                task_data = data.get("data", {})
                if isinstance(task_data, list) and len(task_data) > 0:
                    task_data = task_data[0]

                status = task_data.get("status", "processing")
                state = task_data.get("state", status)  # Some responses use "state" instead

                # Normalize status
                if state in ("complete", "succeeded", "success"):
                    status = "completed"
                elif state in ("failed", "error"):
                    status = "failed"
                else:
                    status = "processing"

                audio_url = (
                    task_data.get("audio_url")
                    or task_data.get("audio")
                    or task_data.get("url")
                )

                return {
                    "status": status,
                    "audio_url": audio_url,
                    "error": task_data.get("error_message") or task_data.get("error"),
                }

            # Handle error response
            return {
                "status": "failed",
                "audio_url": None,
                "error": data.get("msg", "Unknown error from Suno API"),
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Suno API poll error {e.response.status_code}: {e.response.text[:200]}")
            return {
                "status": "processing",  # Keep polling on error
                "audio_url": None,
                "error": f"HTTP {e.response.status_code}",
            }
        except Exception as e:
            logger.error(f"Error polling Suno API: {e}")
            return {
                "status": "processing",  # Keep polling on error
                "audio_url": None,
                "error": str(e),
            }


async def poll_music_status(task_id: str, ai_service: str = "suno") -> dict:
    if ai_service == "mureka" and settings.has_mureka:
        return await _poll_mureka_task(task_id)
    if ai_service == "suno":
        return await _poll_suno_task(task_id)
    return {"status": "completed", "file_url": MOCK_MP3_URL, "duration": 180.0}
