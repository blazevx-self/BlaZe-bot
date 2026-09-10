from datetime import datetime

from sqlalchemy import func, ForeignKey, Enum as SqlEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger

from app.database.models import Base
from app.core.enums.rp_commands import TypeRpCommand

class RpCommandOrm(Base):
    __tablename__ = 'rp_commands'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            'chats.telegram_id',
            ondelete='CASCADE'
        ),
        index=True,
        nullable=False
    )

    command: Mapped[str] = mapped_column(nullable=False)
    action: Mapped[str] = mapped_column(nullable=False)
    type_command: Mapped[TypeRpCommand] = mapped_column(
        SqlEnum(TypeRpCommand),
        nullable=False
    )

    file_id: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "chat_id",
            "command",
            name="uq_rp_command_chat_command"
        ),
    )

    def to_kwargs(self) -> dict:
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "command": self.command,
            "action": self.action,
            "type_command": self.type_command,
            "file_id": self.file_id,
            "created_at": self.created_at,
        }