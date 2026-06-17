import asyncio
import base64
import logging
import uuid
from typing import List

from sqlalchemy import select

from app.core.config import settings

logger = logging.getLogger(__name__)

MOCK_COVER_URLS = {
    "1:1": "https://picsum.photos/seed/cover11/1024/1024",
    "16:9": "https://picsum.photos/seed/cover169/1920/1080",
    "9:16": "https://picsum.photos/seed/cover916/1080/1920",
}

SIZE_MAP = {
    "1:1": "1024x1024",
    "16:9": "1792x1024",
    "9:16": "1024x1792",
}


async def generate_cover_image(
    prompt_genre: str,
    prompt_mood: str,
    prompt_keywords: str,
    size: str = "1:1",
    ai_model: str = "gpt-image",
) -> str:
    """Generate a cover image. Returns URL. Falls back to mock if no API key."""
    if ai_model == "gpt-image" and settings.has_openai:
        return await _generate_openai_image(
            prompt_genre, prompt_mood, prompt_keywords, size
        )

    logger.info(f"Using mock cover image for size {size}")
    return MOCK_COVER_URLS.get(size, MOCK_COVER_URLS["1:1"])


async def _generate_openai_image(
    prompt_genre: str,
    prompt_mood: str,
    prompt_keywords: str,
    size: str,
) -> str:
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = (
            f"Album cover art for a {prompt_genre} music album. "
            f"Mood: {prompt_mood}. "
            f"Keywords: {prompt_keywords}. "
            f"Professional, high quality, artistic."
        )

        dall_e_size = SIZE_MAP.get(size, "1024x1024")

        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=dall_e_size,
            quality="standard",
            n=1,
        )
        return response.data[0].url

    except Exception as e:
        logger.error(f"OpenAI image generation failed: {e}")
        return MOCK_COVER_URLS.get(size, MOCK_COVER_URLS["1:1"])


async def _process_cover(cover_id: str, db_session_factory) -> None:
    """Background task: generate cover image and update DB."""
    async with db_session_factory() as session:
        try:
            from app.models.cover import Cover

            result = await session.execute(
                select(Cover).where(Cover.id == uuid.UUID(cover_id))
            )
            cover = result.scalar_one_or_none()

            if cover:
                image_url = await generate_cover_image(
                    cover.prompt_genre,
                    cover.prompt_mood,
                    cover.prompt_keywords,
                    cover.size,
                    cover.ai_model,
                )
                cover.image_url = image_url
                cover.image_key = f"covers/{cover_id}_{cover.size.replace(':', 'x')}.png"
                cover.status = "completed"
                await session.commit()
                logger.info(f"Cover {cover_id} ({cover.size}) completed")
        except Exception as e:
            logger.error(f"Cover processing error {cover_id}: {e}")
            await session.rollback()


def start_cover_processing(cover_id: str, background_tasks, db_session_factory) -> None:
    background_tasks.add_task(_process_cover, cover_id, db_session_factory)
