from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SoMeAccount(Base):
    __tablename__ = "some_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(2048), nullable=False, default="")
    country_code: Mapped[str] = mapped_column(String(10), nullable=False)
    uploads_playlist_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    provider_id: Mapped[int | None] = mapped_column(
        ForeignKey("some_providers.id", ondelete="SET NULL"), nullable=True
    )

    provider: Mapped["SoMeProvider | None"] = relationship(  # noqa: F821
        "SoMeProvider", back_populates="accounts", lazy="selectin"
    )
    thumbnails: Mapped[list["SoMeAccountThumbnail"]] = relationship(  # noqa: F821
        "SoMeAccountThumbnail", back_populates="social_media_account_rel", lazy="selectin"
    )
    items: Mapped[list["SoMeAccountItem"]] = relationship(  # noqa: F821
        "SoMeAccountItem", back_populates="social_media_account_rel", lazy="selectin"
    )
