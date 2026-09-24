from datetime import datetime

from sqlalchemy import func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base

class ChatMemberOrm(Base):
    __tablename__ = 'chat_members'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    chat_id: Mapped[int] = mapped_column(
        ForeignKey(
            'chats.id',
            ondelete='CASCADE'
        ),
        index=True,
        nullable=False

    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            'users.id',
            ondelete='CASCADE'
        ),
        index=True,
        nullable=False
    )

    warnings: Mapped[int] = mapped_column(default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            'chat_id',
            'user_id',
            name='uq_chat_member'
        ),
    )