import asyncio
import logging
import uuid

from sqlalchemy import select

logger = logging.getLogger(__name__)

# Platform LUFS targets
PLATFORM_LUFS = {
    "spotify": -14.0,
    "apple_music": -16.0,
    "youtube": -14.0,
    "soundcloud": -10.0,
    "tidal": -14.0,
}

MOCK_OUTPUT_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3"


async def _process_mastering(mastering_id: str, db_session_factory) -> None:
    """Background task: simulate mastering process."""
    await asyncio.sleep(6)

    async with db_session_factory() as session:
        try:
            from app.models.mastering import Mastering

            result = await session.execute(
                select(Mastering).where(Mastering.id == uuid.UUID(mastering_id))
            )
            mastering = result.scalar_one_or_none()

            if mastering:
                mastering.status = "completed"
                mastering.output_url = MOCK_OUTPUT_URL
                mastering.output_key = f"mastered/{mastering_id}.mp3"
                mastering.lufs = PLATFORM_LUFS.get(mastering.platform, -14.0)
                await session.commit()
                logger.info(f"Mastering {mastering_id} completed")
        except Exception as e:
            logger.error(f"Mastering processing error {mastering_id}: {e}")
            await session.rollback()


def start_mastering_processing(
    mastering_id: str, background_tasks, db_session_factory
) -> None:
    background_tasks.add_task(_process_mastering, mastering_id, db_session_factory)
