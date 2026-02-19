"""from datetime import date

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.database import Base


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[int] = mapped_column(String(200), unique=True)
    username: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[int] = mapped_column(String(200))
    balance: Mapped[int]
    role: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[date]"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.database import Base


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[int] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[int] = mapped_column(String(200))

