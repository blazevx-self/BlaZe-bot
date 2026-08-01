from datetime import datetime

from sqlalchemy import func, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger

from app.database.models.base import Base

class ChatOrm(Base):
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)

    title: Mapped[str | None] = mapped_column(nullable=True)
    rules: Mapped[str | None] = mapped_column(nullable=True)
    welcome_message: Mapped[str | None] = mapped_column(nullable=True)
    goodbye_message: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())