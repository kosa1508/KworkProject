from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, ForeignKey, Boolean, DateTime, Text
from datetime import datetime
from src.database import Base


class ItemsOrm(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))

    # Редкость (1-10, где 1 - самая редкая)
    rarity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Цены
    base_price: Mapped[int] = mapped_column(Integer, nullable=False)
    market_price: Mapped[int | None] = mapped_column(Integer)

    # Вес для вероятности (чем выше, тем чаще выпадает)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    # Статистика
    total_opened: Mapped[int] = mapped_column(Integer, default=0)
    last_opened_at: Mapped[datetime | None] = mapped_column(DateTime)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)