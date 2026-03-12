from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.some_account import SoMeAccount
from app.schemas.some_account import SoMeAccountCreate, SoMeAccountUpdate


class CRUDSoMeAccount(CRUDBase[SoMeAccount, SoMeAccountCreate, SoMeAccountUpdate]):
    async def get_by_account_id(self, db: AsyncSession, account_id: str) -> SoMeAccount | None:
        result = await db.execute(
            select(SoMeAccount).where(SoMeAccount.account_id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_by_provider(
        self, db: AsyncSession, provider_id: int, *, skip: int = 0, limit: int = 100
    ) -> list[SoMeAccount]:
        result = await db.execute(
            select(SoMeAccount)
            .where(SoMeAccount.provider_id == provider_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


some_account = CRUDSoMeAccount(SoMeAccount)
