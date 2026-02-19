from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy import Boolean

from src.database import Base


class CasesOrm(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[int]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[str | None] = mapped_column()
