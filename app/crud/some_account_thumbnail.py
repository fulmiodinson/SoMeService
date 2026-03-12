from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.some_account_thumbnail import SoMeAccountThumbnail
from app.schemas.some_account_thumbnail import (
    SoMeAccountThumbnailCreate,
    SoMeAccountThumbnailUpdate,
)


class CRUDSoMeAccountThumbnail(
    CRUDBase[SoMeAccountThumbnail, SoMeAccountThumbnailCreate, SoMeAccountThumbnailUpdate]
):
    async def get_by_account(
        self, db: AsyncSession, account_id: int, *, skip: int = 0, limit: int = 100
    ) -> list[SoMeAccountThumbnail]:
        result = await db.execute(
            select(SoMeAccountThumbnail)
            .where(SoMeAccountThumbnail.social_media_account == account_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_image_path(
        self, db: AsyncSession, *, db_obj: SoMeAccountThumbnail, image_path: str
    ) -> SoMeAccountThumbnail:
        db_obj.image = image_path
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


some_account_thumbnail = CRUDSoMeAccountThumbnail(SoMeAccountThumbnail)
