from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy import ForeignKey

from src.database import Base


class ItemsOrm(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    rarity: Mapped[int]
    base_price: Mapped[int]
