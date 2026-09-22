from datetime import datetime

from sqlalchemy import func, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger

from app.database.models import Base

class TransferOrm(Base):
    __tablename__ = 'transfers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    sender_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.telegram_id",
            ondelete='CASCADE'
        ),
        index=True,
        nullable=False
    )
    receiver_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.telegram_id",
            ondelete='CASCADE'
        ),
        index=True,
        nullable=False
    )

    amount: Mapped[int] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())