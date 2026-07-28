from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger

from app.database.models.base import Base


class UserOrm(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)

    name: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str | None] = mapped_column(nullable=True)

    money: Mapped[int] = mapped_column(default=0)
    donate_money: Mapped[int] = mapped_column(default=0)

    quiz_attempts: Mapped[int] = mapped_column(default=15)
    quiz_reset_at: Mapped[datetime | None] = mapped_column(nullable=True)

    is_admin: Mapped[bool] = mapped_column(default=False)
    is_subscribed: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

