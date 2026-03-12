from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SoMeProvider(Base):
    __tablename__ = "some_providers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    account_url: Mapped[str] = mapped_column(String(2048), nullable=False)

    accounts: Mapped[list["SoMeAccount"]] = relationship(  # noqa: F821
        "SoMeAccount", back_populates="provider", lazy="selectin"
    )
