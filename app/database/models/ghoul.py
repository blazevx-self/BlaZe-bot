from datetime import datetime

from sqlalchemy import func, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger

from app.database.models.base import Base

class GhoulOrm(Base):
    __tablename__ = 'ghouls'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)

    name: Mapped[str] = mapped_column(nullable=False)

    snap_count: Mapped[int] = mapped_column(default=0)
    coffee_count: Mapped[int] = mapped_column(default=0)

    kagune_type: Mapped[str] = mapped_column(String(32), default="unknown")
    kagune_lvl: Mapped[int] = mapped_column(default=0)
    kagune_was_obtained: Mapped[bool] = mapped_column(default=False)

    strength: Mapped[int] = mapped_column(default=1)
    dexterity: Mapped[int] = mapped_column(default=1)
    speed: Mapped[int] = mapped_column(default=1)
    hp: Mapped[int] = mapped_column(default=5)
    regen: Mapped[int] = mapped_column(default=5)

    became_ghoul_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

