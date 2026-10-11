from datetime import datetime

from sqlalchemy import func, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger

from app.database.models import Base

class ScheduledNotificationOrm(Base):
    __tablename__ = "scheduled_notification"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.telegram_id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    notification_type: Mapped[str] = mapped_column(nullable=False)
    threshold: Mapped[int | None] = mapped_column(nullable=True)

    fire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "telegram_id",
            "notification_type",
            name="unique_notification_telegram_type"
        ),
    )