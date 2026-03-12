from pydantic import BaseModel


class SoMeAccountThumbnailBase(BaseModel):
    social_media_account: int
    type: str
    width: int
    height: int


class SoMeAccountThumbnailCreate(SoMeAccountThumbnailBase):
    pass


class SoMeAccountThumbnailUpdate(BaseModel):
    type: str | None = None
    width: int | None = None
    height: int | None = None


class SoMeAccountThumbnailRead(SoMeAccountThumbnailBase):
    id: int
    image: str | None

    model_config = {"from_attributes": True}
