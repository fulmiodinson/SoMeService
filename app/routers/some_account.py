from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.keycloak import get_current_token
from app.crud import some_account as crud
from app.database import get_db
from app.schemas.some_account import SoMeAccountCreate, SoMeAccountRead, SoMeAccountUpdate

router = APIRouter(prefix="/accounts", tags=["accounts"])

Auth = Annotated[dict[str, Any], Depends(get_current_token)]
DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_model=list[SoMeAccountRead])
async def list_accounts(
    _: Auth,
    db: DB,
    skip: int = 0,
    limit: int = 100,
    provider_id: int | None = None,
) -> list[SoMeAccountRead]:
    if provider_id is not None:
        return await crud.get_by_provider(db, provider_id, skip=skip, limit=limit)
    return await crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=SoMeAccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    _: Auth,
    db: DB,
    payload: SoMeAccountCreate,
) -> SoMeAccountRead:
    existing = await crud.get_by_account_id(db, payload.account_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Account with account_id '{payload.account_id}' already exists.",
        )
    return await crud.create(db, obj_in=payload)


@router.get("/{account_id}", response_model=SoMeAccountRead)
async def get_account(_: Auth, db: DB, account_id: int) -> SoMeAccountRead:
    obj = await crud.get(db, account_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")
    return obj


@router.patch("/{account_id}", response_model=SoMeAccountRead)
async def update_account(
    _: Auth,
    db: DB,
    account_id: int,
    payload: SoMeAccountUpdate,
) -> SoMeAccountRead:
    obj = await crud.get(db, account_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")
    return await crud.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(_: Auth, db: DB, account_id: int) -> None:
    obj = await crud.remove(db, id=account_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")
