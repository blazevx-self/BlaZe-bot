from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models import Base
from app.database.models.common.user import UserOrm

class LotteryOrm(Base):
    __tablename__ = "lotteries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            UserOrm.telegram_id,
            ondelete="CASCADE"
        ),
        nullable=False
    )

    bet_amount: Mapped[int] = mapped_column(nullable=False)

    chosen_color: Mapped[str] = mapped_column(nullable=False)
    winning_color: Mapped[str] = mapped_column(nullable=False)

    is_won: Mapped[bool] = mapped_column(default=False, nullable=False)
    earned: Mapped[int] = mapped_column(default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())