from pydantic import BaseModel, HttpUrl


class SoMeProviderBase(BaseModel):
    name: str
    account_url: str


class SoMeProviderCreate(SoMeProviderBase):
    pass


class SoMeProviderUpdate(BaseModel):
    name: str | None = None
    account_url: str | None = None


class SoMeProviderRead(SoMeProviderBase):
    id: int

    model_config = {"from_attributes": True}
