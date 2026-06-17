import logging
import os
import uuid
from pathlib import Path
from typing import Optional

import aiofiles

from app.core.config import settings

logger = logging.getLogger(__name__)

UPLOADS_DIR = Path("/app/uploads")


def _ensure_uploads_dir() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def _local_file_url(key: str) -> str:
    return f"/files/local/{key}"


async def upload_file(file_content: bytes, key: str, content_type: str = "application/octet-stream") -> str:
    """Upload file to S3 or local filesystem fallback. Returns public URL."""
    if settings.has_s3:
        return await _upload_to_s3(file_content, key, content_type)
    return await _upload_to_local(file_content, key)


async def _upload_to_s3(file_content: bytes, key: str, content_type: str) -> str:
    try:
        import boto3
        from botocore.exceptions import ClientError

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=file_content,
            ContentType=content_type,
        )
        url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        logger.info(f"Uploaded to S3: {key}")
        return url
    except Exception as e:
        logger.error(f"S3 upload failed, falling back to local: {e}")
        return await _upload_to_local(file_content, key)


async def _upload_to_local(file_content: bytes, key: str) -> str:
    _ensure_uploads_dir()
    safe_key = key.replace("/", "_")
    file_path = UPLOADS_DIR / safe_key
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_content)
    logger.info(f"Saved locally: {file_path}")
    return _local_file_url(safe_key)


async def generate_presigned_url(key: str, expires: int = 900) -> str:
    """Generate presigned URL or return local URL."""
    if settings.has_s3:
        try:
            import boto3

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key},
                ExpiresIn=expires,
            )
            return url
        except Exception as e:
            logger.error(f"Presigned URL generation failed: {e}")

    safe_key = key.replace("/", "_")
    return _local_file_url(safe_key)


async def delete_file(key: str) -> bool:
    """Delete file from S3 or local filesystem."""
    if settings.has_s3:
        try:
            import boto3

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
            return True
        except Exception as e:
            logger.error(f"S3 delete failed: {e}")
            return False

    safe_key = key.replace("/", "_")
    file_path = UPLOADS_DIR / safe_key
    if file_path.exists():
        file_path.unlink()
    return True


def generate_file_key(prefix: str, filename: str) -> str:
    """Generate a unique S3 key for a file."""
    ext = Path(filename).suffix
    unique_id = str(uuid.uuid4())
    return f"{prefix}/{unique_id}{ext}"
