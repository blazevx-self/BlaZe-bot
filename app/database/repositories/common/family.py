from datetime import datetime

from sqlalchemy import (
    select, insert, update,
    func, or_, delete
)

from app.database.repositories.base import Base
from app.database.models import ChatOrm
from app.database.models.chat.chat_member import ChatMemberOrm
from app.database.models.common.family import (
    FamilyOrm, FamilyProposalOrm,
    FamilyRenameOrm, FamilyMemberOrm
)

from app.core.exceptions.chat import FamilyNotFoundError

class FamilyRepository(Base):
    async def get(self, family_id: int) -> FamilyOrm | None:
        return await self.session.get(FamilyOrm, family_id)

    async def create(self) -> FamilyOrm:
        family = FamilyOrm()
        self.session.add(family)
        await self.session.flush()
        return family

    async def set_name(self, family_id: int, name: str) -> None:
        stmt = (
            update(FamilyOrm)
            .where(FamilyOrm.id == family_id)
            .values(name=name)
        )
        await self.session.execute(stmt)

    async def family_id_of(self, user_id) -> int | None:
        stmt = select(FamilyMemberOrm.family_id).where(
            FamilyMemberOrm.user_id == user_id
        )
        return await self.session.scalar(stmt)

    async def list_members(self, family_id: int) -> list[FamilyMemberOrm]:
        stmt = (
            select(FamilyMemberOrm)
            .where(FamilyMemberOrm.family_id == family_id)
            .order_by(FamilyMemberOrm.joined_at, FamilyMemberOrm.user_id)
        )

        rows = await self.session.scalars(stmt)

        return list(rows)

    async def add_member(self, family_id: int, user_id: int) -> None:
        stmt = insert(FamilyMemberOrm).values(
            family_id=family_id,
            user_id=user_id
        )
        await self.session.execute(stmt)

    async def count_members(self, family_id: int) -> int:
        stmt = (
            select(func.count(FamilyMemberOrm.user_id))
            .where(FamilyMemberOrm.family_id == family_id)
        )

        result = await self.session.scalar(stmt)

        return result if result is not None else 0

    async def families_in_chat(self, telegram_chat_id: int) -> list[FamilyOrm]:
        chat = await self.session.scalar(
            select(ChatOrm).where(ChatOrm.telegram_id == telegram_chat_id)
        )

        if chat is None:
            return []

        user_ids = select(ChatMemberOrm.user_id).where(
            ChatMemberOrm.chat_id == chat.id
        )

        family_ids = select(FamilyMemberOrm.family_id).where(
            FamilyMemberOrm.user_id.in_(user_ids)
        )

        stmt = select(FamilyOrm).where(
            FamilyOrm.id.in_(family_ids),
            FamilyOrm.dissolved_at.is_(None),
        )

        rows = await self.session.scalars(stmt)
        return list(rows)

    async def create_proposal(
        self,
        initiator_user_id: int,
        target_user_id: int,
        chat_id: int,
        expires_at: datetime,
    ) -> FamilyProposalOrm:
        proposal = FamilyProposalOrm(
            initiator_user_id=initiator_user_id,
            target_user_id=target_user_id,
            chat_id=chat_id,
            expires_at=expires_at,
            stage="offer"
        )

        self.session.add(proposal)
        await self.session.flush()

        return proposal

    async def get_proposal(self, proposal_id: int) -> FamilyProposalOrm | None:
        return await self.session.get(FamilyProposalOrm, proposal_id)

    async def set_message_id(self, proposal_id: int, message_id: int) -> None:
        stmt = (
            update(FamilyProposalOrm)
            .where(FamilyProposalOrm.id == proposal_id)
            .values(message_id=message_id)
        )
        await self.session.execute(stmt)

    async def has_active(self, initiator_user_id: int, target_user_id: int) -> bool:
        stmt = select(FamilyProposalOrm.id).where(
            FamilyProposalOrm.initiator_user_id == initiator_user_id,
            FamilyProposalOrm.target_user_id == target_user_id,
            or_(
                FamilyProposalOrm.stage == "offer",
                FamilyProposalOrm.stage == "awaiting",
            ),
        )
        return await self.session.scalar(stmt) is not None

    async def set_initiator_ok(self, proposal_id: int) -> None:
        stmt = (
            update(FamilyProposalOrm)
            .where(FamilyProposalOrm.id == proposal_id)
            .values(initiator_ok=True)
        )
        await self.session.execute(stmt)

    async def set_target_ok(self, proposal_id: int) -> None:
        stmt = (
            update(FamilyProposalOrm)
            .where(FamilyProposalOrm.id == proposal_id)
            .values(target_ok=True)
        )
        await self.session.execute(stmt)

    async def set_stage(
        self,
        proposal_id: int,
        stage: str,
        declined_by: int | None = None
    ) -> None:
        values: dict = {"stage": stage}

        if declined_by is not None:
            values["declined_by"] = declined_by

        stmt = (
            update(FamilyProposalOrm)
            .where(FamilyProposalOrm.id == proposal_id)
            .values(**values)
        )

        await self.session.execute(stmt)

    async def expired_ids(self) -> list[int]:
        stmt = select(FamilyProposalOrm.id).where(
            or_(
                FamilyProposalOrm.stage == "offer",
                FamilyProposalOrm.stage == "awaiting",
            ),
            FamilyProposalOrm.expires_at < func.now()
        )

        rows = await self.session.scalars(stmt)
        return list(rows)

    async def create_rename(
        self,
        family_id: int,
        name: str,
        proposer_user_id: int,
        chat_id: int,
        expires_at: datetime
    ) -> FamilyRenameOrm:
        rename = FamilyRenameOrm(
            family_id=family_id,
            name=name,
            proposer_user_id=proposer_user_id,
            chat_id=chat_id,
            expires_at=expires_at,
            stage="awaiting"
        )
        self.session.add(rename)
        await self.session.flush()
        return rename

    async def get_rename(self, rename_id: int) -> FamilyRenameOrm | None:
        return await self.session.get(FamilyRenameOrm, rename_id)

    async def has_awaiting_rename(self, family_id: int) -> bool:
        stmt = select(FamilyRenameOrm.id).where(
            FamilyRenameOrm.family_id == family_id,
            FamilyRenameOrm.stage == "awaiting"
        )
        return await self.session.scalar(stmt) is not None

    async def set_rename_message_id(self, rename_id: int, message_id: int) -> None:
        stmt = (
            update(FamilyRenameOrm)
            .where(FamilyRenameOrm.id == rename_id)
            .values(message_id=message_id)
        )
        await self.session.execute(stmt)

    async def set_other_ok(self, rename_id: int) -> None:
        stmt = (
            update(FamilyRenameOrm)
            .where(FamilyRenameOrm.id == rename_id)
            .values(other_ok=True)
        )
        await self.session.execute(stmt)

    async def finish_rename(
        self,
        rename_id: int,
        stage: str,
        declined_by: int | None = None,
    ) -> None:
        values: dict = {"stage": stage}

        if declined_by is not None:
            values["declined_by"] = declined_by

        stmt = (
            update(FamilyRenameOrm)
            .where(FamilyRenameOrm.id == rename_id)
            .values(**values)
        )

        await self.session.execute(stmt)

    async def expired_rename_ids(self) -> list[int]:
        stmt = select(FamilyRenameOrm.id).where(
            FamilyRenameOrm.stage == "awaiting",
            FamilyRenameOrm.expires_at < func.now()
        )

        rows = await self.session.scalars(stmt)
        return list(rows)

    async def change_balance(self, family_id, delta: int) -> int:
        stmt = (
            update(FamilyOrm)
            .where(FamilyOrm.id == family_id)
            .values(money=FamilyOrm.money + delta)
            .returning(FamilyOrm.money)
        )

        result = await self.session.scalar(stmt)

        if result is None:
            raise FamilyNotFoundError(f"Family ({family_id}) not found")

        return result

    async def remove_member(self, user_id) -> None:
        stmt = delete(FamilyMemberOrm).where(FamilyMemberOrm.user_id == user_id)
        await self.session.execute(stmt)

    async def dissolve(self, family_id: int) -> int:
        money = await self.session.scalar(
            select(FamilyOrm.money).where(FamilyOrm.id == family_id)
        )

        if money is None:
            raise FamilyNotFoundError(f"Family ({family_id}) not found")

        await self.session.execute(
            update(FamilyOrm)
            .where(FamilyOrm.id == family_id)
            .values(money=0, dissolved_at=func.now())
        )

        return money