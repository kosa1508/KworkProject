from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, BigInteger, DateTime, Float
from datetime import datetime
from src.database import Base


class CaseOpeningsOrm(Base):
    __tablename__ = "case_openings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))

    # Криптографические данные для верификации
    server_seed: Mapped[str] = mapped_column(String(64))  # Серверный сид
    client_seed: Mapped[str] = mapped_column(String(64))  # Клиентский сид
    nonce: Mapped[int] = mapped_column(BigInteger)  # Счетчик
    roll: Mapped[int] = mapped_column()  # Результат от 0 до 999999

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)