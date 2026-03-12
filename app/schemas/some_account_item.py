from datetime import datetime

from pydantic import BaseModel


class SoMeAccountItemBase(BaseModel):
    social_media_account: int
    item_id: str
    type: str
    title: str
    description: str = ""
    published: datetime


class SoMeAccountItemCreate(SoMeAccountItemBase):
    pass


class SoMeAccountItemUpdate(BaseModel):
    item_id: str | None = None
    type: str | None = None
    title: str | None = None
    description: str | None = None
    published: datetime | None = None


class SoMeAccountItemRead(SoMeAccountItemBase):
    id: int

    model_config = {"from_attributes": True}
