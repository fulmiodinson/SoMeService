from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.some_account_item import SoMeAccountItem
from app.schemas.some_account_item import SoMeAccountItemCreate, SoMeAccountItemUpdate


class CRUDSoMeAccountItem(
    CRUDBase[SoMeAccountItem, SoMeAccountItemCreate, SoMeAccountItemUpdate]
):
    async def get_by_item_id(self, db: AsyncSession, item_id: str) -> SoMeAccountItem | None:
        result = await db.execute(
            select(SoMeAccountItem).where(SoMeAccountItem.item_id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_by_account(
        self,
        db: AsyncSession,
        account_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        type_filter: str | None = None,
    ) -> list[SoMeAccountItem]:
        query = select(SoMeAccountItem).where(
            SoMeAccountItem.social_media_account == account_id
        )
        if type_filter:
            query = query.where(SoMeAccountItem.type == type_filter)
        query = query.order_by(SoMeAccountItem.published.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())


some_account_item = CRUDSoMeAccountItem(SoMeAccountItem)
