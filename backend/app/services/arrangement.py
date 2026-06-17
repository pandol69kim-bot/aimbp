import asyncio
import logging
import uuid

from sqlalchemy import select

logger = logging.getLogger(__name__)

MOCK_MP3_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
MOCK_WAV_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
MOCK_STEMS = {
    "drum": MOCK_MP3_URL,
    "bass": MOCK_MP3_URL,
    "melody": MOCK_MP3_URL,
    "chord": MOCK_MP3_URL,
}


async def _process_arrangement(arrangement_id: str, db_session_factory) -> None:
    """Background task: simulate arrangement processing."""
    await asyncio.sleep(3)

    async with db_session_factory() as session:
        try:
            from app.models.arrangement import Arrangement

            result = await session.execute(
                select(Arrangement).where(Arrangement.id == uuid.UUID(arrangement_id))
            )
            arrangement = result.scalar_one_or_none()

            if arrangement:
                arrangement.status = "completed"
                arrangement.mp3_url = MOCK_MP3_URL
                arrangement.wav_url = MOCK_WAV_URL
                arrangement.stems = MOCK_STEMS
                await session.commit()
                logger.info(f"Arrangement {arrangement_id} completed")
        except Exception as e:
            logger.error(f"Arrangement processing error {arrangement_id}: {e}")
            await session.rollback()


def start_arrangement_processing(
    arrangement_id: str, background_tasks, db_session_factory
) -> None:
    background_tasks.add_task(_process_arrangement, arrangement_id, db_session_factory)
