import os
import uuid
from pathlib import Path
from typing import Annotated, Any

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.keycloak import get_current_token
from app.config import settings
from app.crud import some_account as account_crud
from app.crud import some_account_thumbnail as crud
from app.database import get_db
from app.schemas.some_account_thumbnail import (
    SoMeAccountThumbnailCreate,
    SoMeAccountThumbnailRead,
    SoMeAccountThumbnailUpdate,
)

router = APIRouter(prefix="/thumbnails", tags=["thumbnails"])

Auth = Annotated[dict[str, Any], Depends(get_current_token)]
DB = Annotated[AsyncSession, Depends(get_db)]

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@router.get("/", response_model=list[SoMeAccountThumbnailRead])
async def list_thumbnails(
    _: Auth,
    db: DB,
    account_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[SoMeAccountThumbnailRead]:
    if account_id is not None:
        return await crud.get_by_account(db, account_id, skip=skip, limit=limit)
    return await crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=SoMeAccountThumbnailRead, status_code=status.HTTP_201_CREATED)
async def create_thumbnail(
    _: Auth,
    db: DB,
    payload: SoMeAccountThumbnailCreate,
) -> SoMeAccountThumbnailRead:
    account = await account_crud.get(db, payload.social_media_account)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id {payload.social_media_account} not found.",
        )
    return await crud.create(db, obj_in=payload)


@router.get("/{thumbnail_id}", response_model=SoMeAccountThumbnailRead)
async def get_thumbnail(_: Auth, db: DB, thumbnail_id: int) -> SoMeAccountThumbnailRead:
    obj = await crud.get(db, thumbnail_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found."
        )
    return obj


@router.patch("/{thumbnail_id}", response_model=SoMeAccountThumbnailRead)
async def update_thumbnail(
    _: Auth,
    db: DB,
    thumbnail_id: int,
    payload: SoMeAccountThumbnailUpdate,
) -> SoMeAccountThumbnailRead:
    obj = await crud.get(db, thumbnail_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found."
        )
    return await crud.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{thumbnail_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thumbnail(_: Auth, db: DB, thumbnail_id: int) -> None:
    obj = await crud.remove(db, id=thumbnail_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found."
        )
    # Clean up stored image file if present
    if obj.image:
        image_path = Path(settings.media_root) / obj.image
        if image_path.exists():
            image_path.unlink(missing_ok=True)


@router.post(
    "/{thumbnail_id}/image",
    response_model=SoMeAccountThumbnailRead,
    summary="Upload or replace the image file for a thumbnail",
)
async def upload_thumbnail_image(
    _: Auth,
    db: DB,
    thumbnail_id: int,
    file: UploadFile,
) -> SoMeAccountThumbnailRead:
    obj = await crud.get(db, thumbnail_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found."
        )

    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image type '{file.content_type}'. "
            f"Allowed: {', '.join(sorted(_ALLOWED_CONTENT_TYPES))}",
        )

    ext = (file.filename or "image").rsplit(".", 1)[-1].lower()
    safe_ext = ext if ext in {"jpg", "jpeg", "png", "webp", "gif"} else "bin"
    relative_path = f"thumbnails/{obj.social_media_account}/{uuid.uuid4().hex}.{safe_ext}"
    dest = Path(settings.media_root) / relative_path
    dest.parent.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(dest, "wb") as out_file:
        while chunk := await file.read(1024 * 256):  # 256 KB chunks
            await out_file.write(chunk)

    # Remove previous image file if it exists
    if obj.image and obj.image != relative_path:
        old_path = Path(settings.media_root) / obj.image
        old_path.unlink(missing_ok=True)

    return await crud.update_image_path(db, db_obj=obj, image_path=relative_path)
