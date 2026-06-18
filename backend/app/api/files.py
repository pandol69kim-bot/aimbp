import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.s3 import upload_file, generate_presigned_url, delete_file, generate_file_key, UPLOADS_DIR

router = APIRouter(prefix="/files", tags=["files"])

# In-memory file registry (in production use DB table)
_file_registry: dict[str, dict] = {}


def _ok(data: Any) -> dict:
    return {"success": True, "data": data, "error": None}


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    if len(content) > 100 * 1024 * 1024:  # 100MB limit
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large (max 100MB)",
        )

    file_id = str(uuid.uuid4())
    key = generate_file_key(f"uploads/{current_user.id}", file.filename or "file")
    content_type = file.content_type or "application/octet-stream"

    file_url = await upload_file(content, key, content_type)

    _file_registry[file_id] = {
        "file_id": file_id,
        "file_url": file_url,
        "file_key": key,
        "filename": file.filename,
        "content_type": content_type,
        "user_id": str(current_user.id),
    }

    return _ok(
        {
            "file_id": file_id,
            "file_url": file_url,
            "file_key": key,
        }
    )


@router.get("/{file_id}/url")
async def get_file_url(
    file_id: str,
    current_user: User = Depends(get_current_user),
):
    file_info = _file_registry.get(file_id)
    if not file_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    if file_info["user_id"] != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    url = await generate_presigned_url(file_info["file_key"])
    return _ok({"url": url})


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_endpoint(
    file_id: str,
    current_user: User = Depends(get_current_user),
):
    file_info = _file_registry.get(file_id)
    if not file_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    if file_info["user_id"] != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    await delete_file(file_info["file_key"])
    del _file_registry[file_id]


@router.get("/local/{filename:path}")
async def serve_local_file(filename: str):
    """Serve locally stored files (dev mode fallback)."""
    file_path = UPLOADS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(str(file_path))
