import json
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

MOCK_LYRICS = {
    "korean": {
        "verse": (
            "어둠 속에서 빛을 찾아\n"
            "긴 밤을 걸어왔어\n"
            "수많은 시간들이 흘러\n"
            "이제야 알 것 같아"
        ),
        "chorus": (
            "날아올라 끝없는 하늘로\n"
            "두려움을 뒤로하고\n"
            "새로운 세상을 향해\n"
            "나는 날아가"
        ),
        "bridge": (
            "포기하지 마\n"
            "아직 끝이 아니야\n"
            "다시 일어서\n"
            "빛이 되어줄게"
        ),
        "hook": "날아올라, 날아올라, 끝없이",
    },
    "english": {
        "verse": (
            "Walking through the shadows alone\n"
            "Searching for a light to guide\n"
            "All these moments I have known\n"
            "Drifting with the changing tide"
        ),
        "chorus": (
            "Rise up, rise up into the sky\n"
            "Leave the fear behind\n"
            "Spread your wings and fly\n"
            "Towards the morning light"
        ),
        "bridge": (
            "Don't give up now\n"
            "It's not the end\n"
            "Stand up again\n"
            "I'll be your light"
        ),
        "hook": "Rise up, rise up, endlessly",
    },
}


def _get_mock_lyrics(language: str) -> dict:
    lang_key = "korean" if language.lower() in ("korean", "ko") else "english"
    return MOCK_LYRICS[lang_key]


async def generate_lyrics_openai(
    title: str,
    prompt_subject: str,
    prompt_mood: str,
    prompt_genre: str,
    prompt_artist_style: str,
    prompt_language: str,
) -> dict:
    if not settings.has_openai:
        logger.warning("OpenAI API key not set; returning mock lyrics")
        return _get_mock_lyrics(prompt_language)

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        system_prompt = (
            "You are a professional songwriter. "
            "Generate lyrics in JSON format with keys: verse, chorus, bridge, hook. "
            "Each section should be 4-8 lines. "
            "Return only valid JSON, no markdown."
        )

        user_prompt = (
            f"Write song lyrics for:\n"
            f"Title: {title}\n"
            f"Subject: {prompt_subject}\n"
            f"Mood: {prompt_mood}\n"
            f"Genre: {prompt_genre}\n"
            f"Artist style: {prompt_artist_style}\n"
            f"Language: {prompt_language}\n"
            f"\nReturn JSON with keys: verse, chorus, bridge, hook"
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=1500,
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return {
            "verse": data.get("verse", ""),
            "chorus": data.get("chorus", ""),
            "bridge": data.get("bridge", ""),
            "hook": data.get("hook", ""),
        }

    except Exception as e:
        logger.error(f"OpenAI lyrics generation failed: {e}")
        return _get_mock_lyrics(prompt_language)


async def generate_lyrics_claude(
    title: str,
    prompt_subject: str,
    prompt_mood: str,
    prompt_genre: str,
    prompt_artist_style: str,
    prompt_language: str,
) -> dict:
    if not settings.has_anthropic:
        logger.warning("Anthropic API key not set; returning mock lyrics")
        return _get_mock_lyrics(prompt_language)

    try:
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

        user_prompt = (
            f"Write song lyrics for the following song and return ONLY valid JSON "
            f"with keys: verse, chorus, bridge, hook. No markdown, no explanation.\n\n"
            f"Title: {title}\n"
            f"Subject: {prompt_subject}\n"
            f"Mood: {prompt_mood}\n"
            f"Genre: {prompt_genre}\n"
            f"Artist style: {prompt_artist_style}\n"
            f"Language: {prompt_language}"
        )

        message = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            messages=[{"role": "user", "content": user_prompt}],
        )

        content = message.content[0].text
        # Strip any markdown fences if present
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])

        data = json.loads(content)
        return {
            "verse": data.get("verse", ""),
            "chorus": data.get("chorus", ""),
            "bridge": data.get("bridge", ""),
            "hook": data.get("hook", ""),
        }

    except Exception as e:
        logger.error(f"Anthropic lyrics generation failed: {e}")
        return _get_mock_lyrics(prompt_language)


async def generate_lyrics(
    title: str,
    prompt_subject: str,
    prompt_mood: str,
    prompt_genre: str,
    prompt_artist_style: str,
    prompt_language: str,
    ai_model: str = "openai",
) -> dict:
    if ai_model == "claude":
        return await generate_lyrics_claude(
            title, prompt_subject, prompt_mood, prompt_genre, prompt_artist_style, prompt_language
        )
    return await generate_lyrics_openai(
        title, prompt_subject, prompt_mood, prompt_genre, prompt_artist_style, prompt_language
    )
