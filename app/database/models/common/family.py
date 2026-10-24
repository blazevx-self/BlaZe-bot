from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base

class FamilyOrm(Base):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(nullable=True)

    money: Mapped[int] = mapped_column(BigInteger, default=0)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    dissolved_at: Mapped[datetime | None] = mapped_column(nullable=True)

class FamilyMemberOrm(Base):
    __tablename__ = "family_members"

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    family_id: Mapped[int] = mapped_column(
        ForeignKey(
            "families.id",
            ondelete="CASCADE"
        ),
        index=True
    )

    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())

class FamilyProposalOrm(Base):
    __tablename__ = "family_proposals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    initiator_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    target_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    family_id: Mapped[int | None] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"), nullable=True
    )

    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    initiator_ok: Mapped[bool] = mapped_column(default=False, nullable=False)
    target_ok: Mapped[bool] = mapped_column(default=False, nullable=False)

    stage: Mapped[str] = mapped_column(nullable=False, default="offer")
    declined_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

class FamilyRenameOrm(Base):
    __tablename__ = "family_renames"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(nullable=False)

    proposer_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    other_ok: Mapped[bool] = mapped_column(default=False, nullable=False)

    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    stage: Mapped[str] = mapped_column(nullable=False, default="awaiting")
    declined_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())