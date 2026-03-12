from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://someservice:someservice@db:5432/someservice"

    keycloak_url: str
    keycloak_realm: str
    keycloak_client_id: str = ""

    media_root: str = "/app/media"
    media_url: str = "/media/"

    debug: bool = False

    @property
    def keycloak_issuer(self) -> str:
        return f"{self.keycloak_url}/realms/{self.keycloak_realm}"

    @property
    def keycloak_jwks_uri(self) -> str:
        return f"{self.keycloak_issuer}/protocol/openid-connect/certs"


settings = Settings()
