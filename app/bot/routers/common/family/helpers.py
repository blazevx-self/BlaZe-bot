import html

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from app.configs.yaml_loader import cfg
from app.core.exceptions.chat import FamilyError

from app.database.models.common.family import FamilyProposalOrm
from app.database.models.common.user import UserOrm
from app.database.repositories.common.user import UserRepository

from app.services.common.family import FamilyService
from app.bot.keyboards.common.family import proposal_kb

FAM = cfg["message"]["family"]

def _mention(user: UserOrm) -> str:
    return f'<a href="tg://user?id={user.telegram_id}">{html.escape(user.name)}</a>'

def _invite(
    initiator: UserOrm,
    target: UserOrm,
    initiator_ok: bool,
    target_ok: bool,
) -> str:
    init = _mention(initiator)
    tgt = _mention(target)

    rows = "\n".join((
        FAM["row_ok" if initiator_ok else "row_wait"].format(name=init),
        FAM["row_ok" if target_ok else "row_wait"].format(name=tgt),
    ))

    return FAM["invite"].format(initiator=init, target=tgt, rows=rows)

def _username(bot: Bot) -> str:
    me = getattr(bot, "_me", None)
    return me.username or "" if me else ""

def _kb(
    proposal: FamilyProposalOrm,
    initiator: UserOrm,
    target: UserOrm,
    username: str,
):
    return proposal_kb(
        proposal.id,
        initiator.telegram_id,
        target.telegram_id,
        username,
        initiator_ok=proposal.initiator_ok,
        target_ok=proposal.target_ok,
    )

async def _edit(message: Message, text: str, markup=None) -> None:
    try:
        await message.edit_text(text, reply_markup=markup)
    except TelegramBadRequest:
        pass

async def _pair(
    family_service: FamilyService,
    user_repo: UserRepository,
    proposal_id: int,
):
    proposal = await family_service.get_proposal(proposal_id)
    initiator = await user_repo.get_by_id(proposal.initiator_user_id)
    target = await user_repo.get_by_id(proposal.target_user_id)

    if initiator is None or target is None:
        raise FamilyError(FAM["not_found"])

    return proposal, initiator, target

async def _sync_group(
    bot: Bot,
    proposal: FamilyProposalOrm,
    origin: Message,
    text: str,
    markup=None,
) -> None:
    if proposal.message_id is None:
        return

    if origin.chat.id == proposal.chat_id and origin.message_id == proposal.message_id:
        return

    try:
        await bot.edit_message_text(
            chat_id=proposal.chat_id,
            message_id=proposal.message_id,
            text=text,
            reply_markup=markup,
        )
    except TelegramBadRequest:
        pass

def _other_id(members, proposer_id: int) -> int | None:
    for m in members:
        if m.user_id != proposer_id:
            return m.user_id

    return None