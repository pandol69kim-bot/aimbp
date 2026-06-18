from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://aimbp:aimbp1234@localhost:5432/aimbp"
    DATABASE_URL_SYNC: str = "postgresql://aimbp:aimbp1234@localhost:5432/aimbp"

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI
    OPENAI_API_KEY: str = ""

    # HuggingFace
    HF_API_TOKEN: str = ""

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # Suno
    SUNO_API_KEY: str = ""
    SUNO_API_BASE: str = "https://api.sunoapi.org"
    BACKEND_CALLBACK_URL: str = "http://localhost:8001"

    # Mureka
    MUREKA_API_KEY: str = ""
    MUREKA_API_BASE: str = "https://api.mureka.ai"

    # ElevenLabs
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_API_BASE: str = "https://api.elevenlabs.io"

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-northeast-2"
    S3_BUCKET_NAME: str = "aimbp-files"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # App
    APP_ENV: str = "development"
    DEBUG: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def has_openai(self) -> bool:
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY != "your-openai-api-key")

    @property
    def has_hf(self) -> bool:
        return bool(self.HF_API_TOKEN and self.HF_API_TOKEN != "your-hf-api-token")

    @property
    def has_anthropic(self) -> bool:
        return bool(self.ANTHROPIC_API_KEY and self.ANTHROPIC_API_KEY != "your-anthropic-api-key")

    @property
    def has_suno(self) -> bool:
        return bool(self.SUNO_API_KEY and self.SUNO_API_KEY != "your-suno-api-key")

    @property
    def has_mureka(self) -> bool:
        return bool(self.MUREKA_API_KEY and self.MUREKA_API_KEY != "your-mureka-api-key")

    @property
    def has_elevenlabs(self) -> bool:
        return bool(self.ELEVENLABS_API_KEY and self.ELEVENLABS_API_KEY != "your-elevenlabs-api-key")

    @property
    def has_s3(self) -> bool:
        return bool(
            self.AWS_ACCESS_KEY_ID
            and self.AWS_SECRET_ACCESS_KEY
            and self.AWS_ACCESS_KEY_ID != "your-aws-access-key"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
