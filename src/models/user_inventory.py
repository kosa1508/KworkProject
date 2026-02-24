from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean, Index
from datetime import datetime
from src.database import Base


class UserInventoryOrm(Base):
    __tablename__ = "user_inventory"
    __table_args__ = (
        Index('ix_inventory_user', 'user_id'),
        Index('ix_inventory_user_item', 'user_id', 'item_id'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    opening_id: Mapped[int] = mapped_column(ForeignKey("case_openings.id"), unique=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))

    item_name: Mapped[str] = mapped_column(String(100))
    item_rarity: Mapped[int] = mapped_column(Integer)
    item_price: Mapped[int] = mapped_column(Integer)

    # Статус предмета
    is_tradable: Mapped[bool] = mapped_column(Boolean, default=True)
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False)
    sold_price: Mapped[int | None] = mapped_column(Integer)
    sold_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)