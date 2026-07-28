from datetime import datetime

from sqlalchemy import func, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger

from app.database.models.base import Base
from app.core.enums.cooldown_action import CooldownAction


class UserCooldownOrm(Base):
    __tablename__ = "user_cooldown"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.telegram_id",
            ondelete="CASCADE"
        ),
        index=True,
        nullable=False
    )

    action: Mapped[CooldownAction] = mapped_column(
        SqlEnum(
            CooldownAction,
            name="cooldown_action"
        ),
        nullable=False
    )

    expires_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())