from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SoMeAccountItem(Base):
    __tablename__ = "some_account_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    social_media_account: Mapped[int] = mapped_column(
        ForeignKey("some_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(String(5000), nullable=False, default="")
    published: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    social_media_account_rel: Mapped["SoMeAccount"] = relationship(  # noqa: F821
        "SoMeAccount", back_populates="items", lazy="selectin"
    )
