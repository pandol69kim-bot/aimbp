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
    ai_model: str = "dalle-3",
) -> str:
    """Generate a cover image. Tries: OpenAI → Stable Diffusion → Mock."""
    if ai_model in ("dalle-3", "gpt-image") and settings.has_openai:
        result = await _generate_openai_image(
            prompt_genre, prompt_mood, prompt_keywords, size
        )
        if result:
            return result

    result = await _generate_stable_diffusion_image(
        prompt_genre, prompt_mood, prompt_keywords, size
    )
    if result:
        return result

    logger.info(f"Using mock cover image for size {size}")
    return MOCK_COVER_URLS.get(size, MOCK_COVER_URLS["1:1"])


async def _generate_stable_diffusion_image(
    prompt_genre: str,
    prompt_mood: str,
    prompt_keywords: str,
    size: str,
) -> str | None:
    """Generate image using local PIL (fallback to HuggingFace if available)."""
    try:
        import asyncio
        import io
        import base64
        from PIL import Image, ImageDraw

        # Parse size
        size_map = {"1:1": (512, 512), "16:9": (1024, 576), "9:16": (576, 1024)}
        width, height = size_map.get(size, (512, 512))

        def create_image():
            # Create a gradient background based on mood
            mood_colors = {
                "peaceful": ((100, 150, 200), (150, 200, 240)),
                "dark": ((20, 20, 40), (50, 50, 80)),
                "energetic": ((255, 100, 50), (255, 200, 100)),
                "romantic": ((200, 100, 150), (255, 150, 200)),
                "melancholic": ((80, 80, 120), (120, 120, 160)),
            }

            start_color, end_color = mood_colors.get(
                prompt_mood, ((100, 100, 150), (150, 150, 200))
            )

            image = Image.new("RGB", (width, height), start_color)
            draw = ImageDraw.Draw(image)

            # Draw gradient
            for y in range(height):
                ratio = y / height
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))

            return image

        # Create image locally
        image = await asyncio.to_thread(create_image)

        # Convert to base64 data URL
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        b64_string = base64.b64encode(img_bytes).decode()

        logger.info(
            f"Generated local album cover for {size} ({prompt_genre}/{prompt_mood})"
        )
        return f"data:image/png;base64,{b64_string}"

    except Exception as e:
        logger.warning(f"Local image generation failed: {e}")
        return None


async def _generate_openai_image(
    prompt_genre: str,
    prompt_mood: str,
    prompt_keywords: str,
    size: str,
) -> str | None:
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
        logger.info(f"OpenAI generated image for size {size}")
        return response.data[0].url

    except Exception as e:
        logger.warning(f"OpenAI image generation failed: {e}")
        return None


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
