from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.keycloak import get_current_token
from app.crud import some_account as account_crud
from app.crud import some_account_item as crud
from app.database import get_db
from app.schemas.some_account_item import (
    SoMeAccountItemCreate,
    SoMeAccountItemRead,
    SoMeAccountItemUpdate,
)

router = APIRouter(prefix="/items", tags=["items"])

Auth = Annotated[dict[str, Any], Depends(get_current_token)]
DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_model=list[SoMeAccountItemRead])
async def list_items(
    _: Auth,
    db: DB,
    account_id: int | None = None,
    type: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[SoMeAccountItemRead]:
    if account_id is not None:
        return await crud.get_by_account(db, account_id, skip=skip, limit=limit, type_filter=type)
    return await crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=SoMeAccountItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    _: Auth,
    db: DB,
    payload: SoMeAccountItemCreate,
) -> SoMeAccountItemRead:
    account = await account_crud.get(db, payload.social_media_account)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id {payload.social_media_account} not found.",
        )
    existing = await crud.get_by_item_id(db, payload.item_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Item with item_id '{payload.item_id}' already exists.",
        )
    return await crud.create(db, obj_in=payload)


@router.get("/{item_id}", response_model=SoMeAccountItemRead)
async def get_item(_: Auth, db: DB, item_id: int) -> SoMeAccountItemRead:
    obj = await crud.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")
    return obj


@router.patch("/{item_id}", response_model=SoMeAccountItemRead)
async def update_item(
    _: Auth,
    db: DB,
    item_id: int,
    payload: SoMeAccountItemUpdate,
) -> SoMeAccountItemRead:
    obj = await crud.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")
    return await crud.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(_: Auth, db: DB, item_id: int) -> None:
    obj = await crud.remove(db, id=item_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")
