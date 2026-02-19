from datetime import date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property

from src.database import Base


class PaymentsOrm(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))# ← исправлено
    price: Mapped[int]
    amount: Mapped[int]
    date: Mapped[date]
    provider: Mapped[str] = mapped_column(String(100))

    def __init__(self, **kwargs):
        # Явно инициализируем все атрибуты
        super().__init__(**kwargs)

    @hybrid_property
    def total_cost(self) -> int:
        return self.price * self.amount


