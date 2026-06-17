import asyncio
import logging
import uuid

from sqlalchemy import select

logger = logging.getLogger(__name__)

MOCK_VOCAL_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"


async def _process_vocal(vocal_id: str, db_session_factory) -> None:
    """Background task: simulate vocal synthesis."""
    await asyncio.sleep(4)

    async with db_session_factory() as session:
        try:
            from app.models.vocal import Vocal

            result = await session.execute(
                select(Vocal).where(Vocal.id == uuid.UUID(vocal_id))
            )
            vocal = result.scalar_one_or_none()

            if vocal:
                vocal.status = "completed"
                vocal.file_url = MOCK_VOCAL_URL
                vocal.file_key = f"vocals/{vocal_id}.mp3"
                await session.commit()
                logger.info(f"Vocal {vocal_id} completed")
        except Exception as e:
            logger.error(f"Vocal processing error {vocal_id}: {e}")
            await session.rollback()


def start_vocal_processing(vocal_id: str, background_tasks, db_session_factory) -> None:
    background_tasks.add_task(_process_vocal, vocal_id, db_session_factory)


SAMPLE_VOCAL_LIBRARY = [
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "name": "Aria",
        "gender": "female",
        "genre": "kpop",
        "sample_url": MOCK_VOCAL_URL,
        "is_active": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000002"),
        "name": "Noah",
        "gender": "male",
        "genre": "rock",
        "sample_url": MOCK_VOCAL_URL,
        "is_active": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000003"),
        "name": "Luna",
        "gender": "female",
        "genre": "edm",
        "sample_url": MOCK_VOCAL_URL,
        "is_active": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000004"),
        "name": "Jay",
        "gender": "male",
        "genre": "rap",
        "sample_url": MOCK_VOCAL_URL,
        "is_active": True,
    },
]
