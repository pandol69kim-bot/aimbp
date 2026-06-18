import asyncio
import logging
import os
import uuid

import httpx
from sqlalchemy import select

from app.core.config import settings

logger = logging.getLogger(__name__)

MOCK_VOCAL_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"

SAMPLE_VOCAL_LIBRARY = [
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000001"),
        "name": "Rachel",
        "gender": "female",
        "genre": "pop",
        "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",
        "description": "차분하고 부드러운 여성 보컬",
        "sample_url": MOCK_VOCAL_URL,
        "is_active": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000002"),
        "name": "Bella",
        "gender": "female",
        "genre": "ballad",
        "elevenlabs_voice_id": "EXAVITQu4vr4xnSDxMaL",
        "description": "따뜻하고 감성적인 여성 보컬",
        "sample_url": MOCK_VOCAL_URL,
        "is_active": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000003"),
        "name": "Adam",
        "gender": "male",
        "genre": "rnb",
        "elevenlabs_voice_id": "pNInz6obpgDQGcFmaJgB",
        "description": "깊고 강렬한 남성 보컬",
        "sample_url": MOCK_VOCAL_URL,
        "is_active": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000004"),
        "name": "Josh",
        "gender": "male",
        "genre": "rock",
        "elevenlabs_voice_id": "TxGEqnHWrfWFTfGW9XjX",
        "description": "힘있고 카리스마 있는 남성 보컬",
        "sample_url": MOCK_VOCAL_URL,
        "is_active": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000005"),
        "name": "Elli",
        "gender": "female",
        "genre": "kpop",
        "elevenlabs_voice_id": "MF3mGyEYCl7XYWbV9V6O",
        "description": "밝고 경쾌한 여성 보컬",
        "sample_url": MOCK_VOCAL_URL,
        "is_active": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000006"),
        "name": "Sam",
        "gender": "male",
        "genre": "hiphop",
        "elevenlabs_voice_id": "yoZ06aMxZJJ28mfd3POQ",
        "description": "허스키하고 개성있는 남성 보컬",
        "sample_url": MOCK_VOCAL_URL,
        "is_active": True,
    },
]


async def _call_elevenlabs_tts(voice_id: str, text: str) -> bytes:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.ELEVENLABS_API_BASE}/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": settings.ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True,
                },
            },
        )
        resp.raise_for_status()
        return resp.content


async def _get_lyrics_text(session, track) -> str:
    if track and track.lyrics_id:
        from app.models.lyrics import Lyrics
        lyrics = await session.get(Lyrics, track.lyrics_id)
        if lyrics:
            parts = [lyrics.verse, lyrics.chorus, lyrics.bridge]
            return "\n\n".join(p for p in parts if p)

    title = track.title if track else "song"
    return f"This is {title}. A beautiful melody fills the air."


async def _process_vocal(vocal_id: str, db_session_factory) -> None:
    async with db_session_factory() as session:
        try:
            from app.models.vocal import Vocal, VocalLibrary
            from app.models.track import Track

            result = await session.execute(
                select(Vocal).where(Vocal.id == uuid.UUID(vocal_id))
            )
            vocal = result.scalar_one_or_none()
            if not vocal:
                return

            vocal.status = "processing"
            track_id = vocal.track_id
            library_id = vocal.library_id
            await session.commit()

            track = await session.get(Track, track_id)
            lyrics_text = await _get_lyrics_text(session, track)
            library = await session.get(VocalLibrary, library_id)

            elevenlabs_voice_id = library.elevenlabs_voice_id if library else None

            if not elevenlabs_voice_id:
                mock_entry = next(
                    (v for v in SAMPLE_VOCAL_LIBRARY if str(v["id"]) == str(library_id)),
                    None,
                )
                elevenlabs_voice_id = mock_entry.get("elevenlabs_voice_id") if mock_entry else None

            if not settings.has_elevenlabs or not elevenlabs_voice_id:
                await asyncio.sleep(2)
                result2 = await session.execute(
                    select(Vocal).where(Vocal.id == uuid.UUID(vocal_id))
                )
                vocal = result2.scalar_one_or_none()
                if vocal:
                    vocal.status = "completed"
                    vocal.file_url = MOCK_VOCAL_URL
                    vocal.file_key = f"vocals/{vocal_id}.mp3"
                    await session.commit()
                logger.info(f"Vocal {vocal_id} completed (mock)")
                return

            mp3_bytes = await _call_elevenlabs_tts(elevenlabs_voice_id, lyrics_text)

            vocals_dir = "/app/uploads/vocals"
            os.makedirs(vocals_dir, exist_ok=True)
            file_path = f"{vocals_dir}/{vocal_id}.mp3"
            with open(file_path, "wb") as f:
                f.write(mp3_bytes)

            result3 = await session.execute(
                select(Vocal).where(Vocal.id == uuid.UUID(vocal_id))
            )
            vocal = result3.scalar_one_or_none()
            if vocal:
                vocal.status = "completed"
                vocal.file_url = f"/api/v1/files/vocals/{vocal_id}.mp3"
                vocal.file_key = f"vocals/{vocal_id}.mp3"
                await session.commit()
            logger.info(f"Vocal {vocal_id} completed via ElevenLabs")

        except Exception as e:
            logger.error(f"Vocal processing error {vocal_id}: {e}")
            try:
                await session.rollback()
                result_err = await session.execute(
                    select(Vocal).where(Vocal.id == uuid.UUID(vocal_id))
                )
                vocal = result_err.scalar_one_or_none()
                if vocal:
                    vocal.status = "failed"
                    vocal.error_message = str(e)[:1024]
                    await session.commit()
            except Exception as inner_e:
                logger.error(f"Failed to update error status for vocal {vocal_id}: {inner_e}")


def start_vocal_processing(vocal_id: str, background_tasks, db_session_factory) -> None:
    background_tasks.add_task(_process_vocal, vocal_id, db_session_factory)
