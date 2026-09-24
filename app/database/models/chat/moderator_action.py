from datetime import datetime

from sqlalchemy import func, ForeignKey, Enum as SqlEnum, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base
from app.core.enums.moderator_action import ModerationActionType

class ModeratorActionOrm(Base):
    __tablename__ = 'moderator_actions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    chat_id: Mapped[int] = mapped_column(
        ForeignKey('chats.id'),
        index=True,
        nullable=False
    )
    moderator_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        index=True,
        nullable=True
    )
    target_user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        index=True,
        nullable=False
    )

    action: Mapped[ModerationActionType] = mapped_column(
        SqlEnum(ModerationActionType),
        nullable=False
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())