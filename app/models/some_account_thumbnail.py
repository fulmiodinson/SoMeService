from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SoMeAccountThumbnail(Base):
    __tablename__ = "some_account_thumbnails"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    social_media_account: Mapped[int] = mapped_column(
        ForeignKey("some_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    # Stores the relative path to the image file, analogous to Django's ImageField
    image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)

    social_media_account_rel: Mapped["SoMeAccount"] = relationship(  # noqa: F821
        "SoMeAccount", back_populates="thumbnails", lazy="selectin"
    )
