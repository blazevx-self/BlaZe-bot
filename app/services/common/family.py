from datetime import datetime, timezone

from app.core.constants.game.family import MARRIAGE_PRICE, PROPOSAL_TTL
from app.core.exceptions.chat import FamilyError
from app.database.models import FamilyRenameOrm

from app.types.services_result.common import ConsentResult, DivorceResult, ProposeResult

from app.database.models.common.family import FamilyProposalOrm
from app.database.models.common.user import UserOrm
from app.database.repositories.common.family import FamilyRepository
from app.database.repositories.common.user import UserRepository

_OPEN = ("offer", "awaiting")

class FamilyService:
    def __init__(
        self,
        family_repo: FamilyRepository,
        user_repo: UserRepository
    ):
        self.family_repo = family_repo
        self.user_repo = user_repo

    async def _user(self, user_id: int) -> UserOrm:
        user = await self.user_repo.get_by_id(user_id)

        if user is None:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Пользователь не найден."
            )

        return user

    async def _proposal(self, proposal_id: int) -> FamilyProposalOrm:
        proposal = await self.family_repo.get_proposal(proposal_id)

        if proposal is None:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Предложение не найдено."
            )

        return proposal

    async def get_proposal(self, proposal_id: int) -> FamilyProposalOrm:
        return await self._proposal(proposal_id)

    @staticmethod
    def _consent(proposal: FamilyProposalOrm, *, done: bool = False) -> ConsentResult:
        return ConsentResult(
            stage=proposal.stage,
            initiator_ok=proposal.initiator_ok,
            target_ok=proposal.target_ok,
            done=done or proposal.stage == "done"
        )

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    async def propose(
        self,
        initiator_id: int,
        target_id: int,
        chat_id: int,
    ) -> ProposeResult:
        if initiator_id == target_id:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Жениться на себе? Сильно конечно, но даже не думай."
            )

        if await self.family_repo.family_id_of(initiator_id) is not None:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Ты уже в семье."
            )

        if await self.family_repo.family_id_of(target_id) is not None:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Этот человек уже в семье."
            )

        if await self.family_repo.has_active(initiator_id, target_id):
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Предложение уже висит."
            )

        if await self.family_repo.has_active(target_id, initiator_id):
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Предложение уже висит."
            )

        initiator = await self._user(initiator_id)
        target = await self._user(target_id)

        if initiator.money < MARRIAGE_PRICE or target.money < MARRIAGE_PRICE:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> " 
                f"Не хватает денег. Брак стоит {MARRIAGE_PRICE} BlaZeCoin с каждого."
            )

        expires_at = self._now() + PROPOSAL_TTL

        proposal = await self.family_repo.create_proposal(
            initiator_user_id=initiator_id,
            target_user_id=target_id,
            chat_id=chat_id,
            expires_at=expires_at
        )

        return ProposeResult(proposal_id=proposal.id, expires_at=expires_at)

    async def set_message_id(self, proposal_id: int, message_id: int) -> None:
        await self.family_repo.set_message_id(proposal_id, message_id)

    async def make_offer(self, proposal_id: int, user_id: int) -> ConsentResult:
        proposal = await self._proposal(proposal_id)

        if proposal.stage != "offer":
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Это предложение уже не актуально."
            )

        if proposal.expires_at <= self._now():
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Предложение истекло."
            )

        if proposal.initiator_user_id != user_id:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Предложение делаешь не ты."
            )

        await self.family_repo.set_stage(proposal_id, "awaiting")
        proposal = await self._proposal(proposal_id)
        return self._consent(proposal)

    async def confirm(self, proposal_id: int, user_id: int) -> ConsentResult:
        proposal = await self._proposal(proposal_id)

        if proposal.stage not in _OPEN:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Это предложение уже не актуально."
            )

        if proposal.expires_at <= self._now():
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Предложение истекло."
            )

        if user_id == proposal.initiator_user_id:
            if proposal.initiator_ok:
                raise FamilyError(
                    "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                    "Ты уже подтвердил."
                )
            await self.family_repo.set_initiator_ok(proposal_id)

        elif user_id == proposal.target_user_id:
            if proposal.target_ok:
                raise FamilyError(
                    "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                    "Ты уже согласился."
                )
            await self.family_repo.set_target_ok(proposal_id)

        else:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Это не твоё предложение."
            )

        proposal = await self._proposal(proposal_id)

        if proposal.initiator_ok and proposal.target_ok:
            return await self._complete(proposal)

        return self._consent(proposal)

    async def decline(self, proposal_id: int, user_id: int) -> ConsentResult:
        proposal = await self._proposal(proposal_id)

        if proposal.stage not in _OPEN:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Это предложение уже не актуально."
            )

        if user_id not in (proposal.initiator_user_id, proposal.target_user_id):
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Это не твоё предложение."
            )

        await self.family_repo.set_stage(
            proposal_id, "declined", declined_by=user_id
        )

        proposal = await self._proposal(proposal_id)
        return self._consent(proposal)

    async def _complete(self, proposal: FamilyProposalOrm) -> ConsentResult:
        initiator_id = proposal.initiator_user_id
        target_id = proposal.target_user_id

        if await self.family_repo.family_id_of(initiator_id) is not None:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Ты уже в семье."
            )

        if await self.family_repo.family_id_of(target_id) is not None:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Этот человек уже в семье."
            )

        initiator = await self._user(initiator_id)
        target = await self._user(target_id)

        if initiator.money < MARRIAGE_PRICE or target.money < MARRIAGE_PRICE:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Не хватает денег. Брак стоит {MARRIAGE_PRICE} BlaZeCoin с каждого."
            )

        family = await self.family_repo.create()

        for member in (initiator, target):
            leftover = member.money - MARRIAGE_PRICE
            await self.user_repo.change_money(member.telegram_id, -member.money)

            if leftover:
                await self.family_repo.change_balance(family.id, leftover)

            await self.family_repo.add_member(family.id, member.id)

        await self.family_repo.set_stage(proposal.id, "done")
        proposal = await self._proposal(proposal.id)
        return self._consent(proposal, done=True)

    async def expire_overdue(self) -> list[FamilyProposalOrm]:
        expired: list[FamilyProposalOrm] = []

        for proposal_id in await self.family_repo.expired_ids():
            await self.family_repo.set_stage(proposal_id, "expired")
            proposal = await self.family_repo.get_proposal(proposal_id)

            if proposal is not None:
                expired.append(proposal)

        return expired

    async def families_in_chat(self, telegram_chat_id: int):
        return await self.family_repo.families_in_chat(telegram_chat_id)

    async def divorce(self, user_id: int) -> DivorceResult:
        family_id = await self.family_repo.family_id_of(user_id)

        if family_id is None:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Ты не в семье."
            )

        family = await self.family_repo.get(family_id)
        total = family.money if family else 0
        taken = total // 2
        inherited = total - taken

        await self.family_repo.remove_member(user_id)

        if await self.family_repo.count_members(family_id) != 1:
            return DivorceResult(heir_id=None, inherited=0, taken=0)

        heir_id = (await self.family_repo.list_members(family_id))[0].user_id

        await self.family_repo.dissolve(family_id)
        await self.family_repo.remove_member(heir_id)

        leaver = await self._user(user_id)
        heir = await self._user(heir_id)

        if taken:
            await self.user_repo.change_money(leaver.telegram_id, taken)
        if inherited:
            await self.user_repo.change_money(heir.telegram_id, inherited)

        return DivorceResult(heir_id=heir_id, inherited=inherited, taken=taken)

    async def get_rename(self, rename_id: int) -> FamilyRenameOrm:
        rename = await self.family_repo.get_rename(rename_id)

        if rename is None:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Предложение имени не найдено."
            )
        return rename

    async def set_rename_message_id(self, rename_id: int, message_id: int) -> None:
        await self.family_repo.set_rename_message_id(rename_id, message_id)

    async def propose_rename(
        self,
        user_id: int,
        raw_name: str,
        chat_id: int
    ) -> FamilyRenameOrm:
        name = " ".join(raw_name.split())

        if not 0 < len(name) <= 32:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Имя семьи — от 1 до 32 символов."
            )

        family_id = await self.family_repo.family_id_of(user_id)

        if family_id is None:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Ты не в семье."
            )

        if await self.family_repo.has_awaiting_rename(family_id):
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Уже решают другое имя."
            )

        members = await self.family_repo.list_members(family_id)

        if len(members) != 2:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Имя меняют вдвоём."
            )

        return await self.family_repo.create_rename(
            family_id=family_id,
            name=name,
            proposer_user_id=user_id,
            chat_id=chat_id,
            expires_at=self._now() + PROPOSAL_TTL,
        )

    async def answer_rename(
        self,
        rename_id: int,
        user_id: int,
        agree: bool,
    ) -> FamilyRenameOrm:
        rename = await self.get_rename(rename_id)

        if rename.stage != "awaiting":
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Это предложение уже не актуально."
            )

        if rename.expires_at <= self._now():
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Предложение истекло."
            )

        if user_id == rename.proposer_user_id:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Ты уже предложил имя."
            )

        members = await self.family_repo.list_members(rename.family_id)
        if user_id not in {m.user_id for m in members}:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Это не твоя семья."
            )

        if not agree:
            await self.family_repo.finish_rename(
                rename_id, "declined", declined_by=user_id
            )
            return await self.get_rename(rename_id)

        await self.family_repo.set_other_ok(rename_id)
        await self.family_repo.set_name(rename.family_id, rename.name)
        await self.family_repo.finish_rename(rename_id, "done")

        return await self.get_rename(rename_id)

    async def balance_of(self, telegram_id: int):
        user = await self.user_repo.get(telegram_id)
        family_id = await self.family_repo.family_id_of(user.id)

        if family_id is None:
            return user.money

        family = await self.family_repo.get(family_id)
        return family.money if family else 0

    async def change_wallet(self, telegram_id: int, delta: int):
        user = await self.user_repo.get(telegram_id)
        family_id = await self.family_repo.family_id_of(user.id)

        if family_id is None:
            return await self.user_repo.change_money(telegram_id, delta)

        family = await self.family_repo.get(family_id)

        if family.money + delta < 0:
            raise FamilyError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Не хватает денег на балансе семьи."
            )
        return await self.family_repo.change_balance(family.id, delta)