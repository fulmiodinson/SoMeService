from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.some_provider import SoMeProvider
from app.schemas.some_provider import SoMeProviderCreate, SoMeProviderUpdate


class CRUDSoMeProvider(CRUDBase[SoMeProvider, SoMeProviderCreate, SoMeProviderUpdate]):
    async def get_by_name(self, db: AsyncSession, name: str) -> SoMeProvider | None:
        result = await db.execute(select(SoMeProvider).where(SoMeProvider.name == name))
        return result.scalar_one_or_none()


some_provider = CRUDSoMeProvider(SoMeProvider)
