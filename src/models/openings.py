from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, BigInteger, Text, Index
from datetime import datetime
from src.database import Base


class CaseOpeningsOrm(Base):
    __tablename__ = "case_openings"
    __table_args__ = (
        Index('ix_openings_user_created', 'user_id', 'created_at'),
        Index('ix_openings_idempotency', 'idempotency_key', unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))

    # Idempotency
    idempotency_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    # Криптографические данные
    server_seed: Mapped[str] = mapped_column(String(64))
    server_seed_hash: Mapped[str] = mapped_column(String(64))  # SHA256 хеш серверного сида
    client_seed: Mapped[str] = mapped_column(String(64))
    nonce: Mapped[int] = mapped_column(BigInteger)
    roll: Mapped[int] = mapped_column(Integer)  # 0-999999

    # Результат
    item_name: Mapped[str] = mapped_column(String(100))
    item_rarity: Mapped[int] = mapped_column(Integer)
    item_price: Mapped[int] = mapped_column(Integer)

    # Статистика
    client_ip: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)