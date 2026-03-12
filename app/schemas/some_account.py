from pydantic import BaseModel


class SoMeAccountBase(BaseModel):
    name: str
    account_id: str
    description: str = ""
    country_code: str
    uploads_playlist_id: str = ""
    provider_id: int | None = None


class SoMeAccountCreate(SoMeAccountBase):
    pass


class SoMeAccountUpdate(BaseModel):
    name: str | None = None
    account_id: str | None = None
    description: str | None = None
    country_code: str | None = None
    uploads_playlist_id: str | None = None
    provider_id: int | None = None


class SoMeAccountRead(SoMeAccountBase):
    id: int

    model_config = {"from_attributes": True}
