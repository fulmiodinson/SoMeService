from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.keycloak import get_current_token
from app.crud import some_provider as crud
from app.database import get_db
from app.schemas.some_provider import SoMeProviderCreate, SoMeProviderRead, SoMeProviderUpdate

router = APIRouter(prefix="/providers", tags=["providers"])

Auth = Annotated[dict[str, Any], Depends(get_current_token)]
DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_model=list[SoMeProviderRead])
async def list_providers(
    _: Auth,
    db: DB,
    skip: int = 0,
    limit: int = 100,
) -> list[SoMeProviderRead]:
    return await crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=SoMeProviderRead, status_code=status.HTTP_201_CREATED)
async def create_provider(
    _: Auth,
    db: DB,
    payload: SoMeProviderCreate,
) -> SoMeProviderRead:
    existing = await crud.get_by_name(db, payload.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Provider with name '{payload.name}' already exists.",
        )
    return await crud.create(db, obj_in=payload)


@router.get("/{provider_id}", response_model=SoMeProviderRead)
async def get_provider(_: Auth, db: DB, provider_id: int) -> SoMeProviderRead:
    obj = await crud.get(db, provider_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found.")
    return obj


@router.patch("/{provider_id}", response_model=SoMeProviderRead)
async def update_provider(
    _: Auth,
    db: DB,
    provider_id: int,
    payload: SoMeProviderUpdate,
) -> SoMeProviderRead:
    obj = await crud.get(db, provider_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found.")
    return await crud.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(_: Auth, db: DB, provider_id: int) -> None:
    obj = await crud.remove(db, id=provider_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found.")
