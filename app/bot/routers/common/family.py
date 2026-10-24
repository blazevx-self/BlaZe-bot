import html

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message

from dependency_injector.wiring import Provide, inject

from app.containers import Container
from app.configs.yaml_loader import cfg

from app.core.constants.game.family import MARRIAGE_PRICE
from app.core.exceptions.chat import FamilyError

from app.types.entities.user import UserData

from app.database.models.common.family import FamilyProposalOrm
from app.database.models.common.user import UserOrm
from app.database.repositories.common.user import UserRepository

from app.services.common.family import FamilyService

from app.bot.keyboards.common.family import offer_kb, proposal_kb, divorce_kb
from app.bot.filters.group_only import GroupOnlyFilter
from app.bot.filters.owner import OwnerCallbackFilter

from app.utils.format_num import format_num

router = Router()

FAM = cfg['message']['family']

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

    if origin.chat.id == proposal.chat_id and  origin.message_id == proposal.message_id:
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

@router.message(F.text.lower() == "брак", GroupOnlyFilter())
@router.message(F.text.lower() == "пожениться", GroupOnlyFilter())
@inject
async def propose_cmd(
    message: Message,
    user: UserData,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    reply = message.reply_to_message

    if not reply or not reply.from_user:
        await message.reply(FAM['usage'])
        return

    if reply.from_user.is_bot:
        await message.reply(FAM['bot'])
        return

    initiator = await user_repo.get(user.telegram_id)
    target = await user_repo.get(reply.from_user.id)

    if initiator is None or target is None:
        await message.reply(FAM['not_found'])
        return

    try:
        result = await family_service.propose(initiator.id, target.id, message.chat.id)
    except FamilyError as e:
        await message.reply(str(e))
        return

    sent = await message.reply(
        FAM["ask"].format(
            initiator=_mention(initiator),
            target=_mention(target),
            price=format_num(MARRIAGE_PRICE),
        ),
        reply_markup=offer_kb(result.proposal_id, initiator.telegram_id),
    )

    await family_service.set_message_id(result.proposal_id, sent.message_id)

@router.callback_query(F.data.startswith("fam_pay_"), OwnerCallbackFilter())
@inject
async def make_offer_cb(
    callback: CallbackQuery,
    user: UserData,
    bot: Bot,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    proposal_id = int(callback.data.split("_")[2])
    me = await user_repo.get(user.telegram_id)

    if me is None:
        await callback.answer(FAM["toast_stale"], show_alert=False)
        return

    try:
        await family_service.make_offer(proposal_id, me.id)
        proposal, initiator, target = await _pair(family_service, user_repo, proposal_id)
    except FamilyError:
        await callback.answer(FAM["toast_stale"], show_alert=False)
        return

    text = _invite(initiator, target, proposal.initiator_ok, proposal.target_ok)

    await _edit(callback.message, text, _kb(proposal, initiator, target, _username(bot)))
    await callback.answer(show_alert=False)

@router.callback_query(F.data.startswith("fam_ok_"), OwnerCallbackFilter())
@inject
async def confirm_cb(
    callback: CallbackQuery,
    user: UserData,
    bot: Bot,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    proposal_id = int(callback.data.split("_")[2])
    me = await user_repo.get(user.telegram_id)

    if me is None:
        await callback.answer(FAM["toast_stale"], show_alert=False)
        return

    try:
        result = await family_service.confirm(proposal_id, me.id)
        proposal, initiator, target = await _pair(family_service, user_repo, proposal_id)
    except FamilyError as e:
        err = str(e)
        toast = FAM["toast_stale"] if ("актуально" in err or "истекло" in err) else None

        await callback.answer(toast, show_alert=False)
        return

    if result.done:
        family_id = await family_service.family_repo.family_id_of(initiator.id)
        family = await family_service.family_repo.get(family_id) if family_id else None

        text = FAM["married"].format(
            members=", ".join((
                _mention(initiator),
                _mention(target),
            )),
            balance=format_num(family.money if family else 0),
        )

        await _edit(callback.message, text)
        await _sync_group(bot, proposal, callback.message, text)
        await callback.answer(FAM["toast_married"], show_alert=False)

        return

    text = _invite(initiator, target, result.initiator_ok, result.target_ok)
    markup = _kb(proposal, initiator, target, _username(bot))

    await _edit(callback.message, text, markup)
    await _sync_group(bot, proposal, callback.message, text, markup)
    await callback.answer(FAM["toast_wait"], show_alert=False)

@router.callback_query(F.data.startswith("fam_no_"))
@inject
async def decline_cb(
    callback: CallbackQuery,
    user: UserData,
    bot: Bot,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    proposal_id = int(callback.data.split("_")[2])
    me = await user_repo.get(user.telegram_id)

    if me is None:
        await callback.answer(FAM["toast_stale"], show_alert=False)
        return

    try:
        await family_service.decline(proposal_id, me.id)
        proposal, initiator, target = await _pair(family_service, user_repo, proposal_id)
    except FamilyError:
        await callback.answer(FAM["not_your_button"], show_alert=False)
        return

    who = initiator if me.id == initiator.id else target
    text = FAM["declined"].format(name=_mention(who))

    await _edit(callback.message, text)
    await _sync_group(bot, proposal, callback.message, text)
    await callback.answer(FAM["toast_declined"], show_alert=False)

@router.message(CommandStart(deep_link=True))
@inject
async def family_deeplink(
    message: Message,
    command: CommandObject,
    user: UserData,
    bot: Bot,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    args = command.args or ""

    if args.startswith("famrn_") or not args.startswith("fam_"):
        return

    try:
        proposal_id = int(args.removeprefix("fam_"))
    except ValueError:
        return

    me = await user_repo.get(user.telegram_id)

    try:
        proposal, initiator, target = await _pair(family_service, user_repo, proposal_id)
    except FamilyError:
        await message.reply(FAM["toast_stale"])
        return

    if me.id not in (proposal.initiator_user_id, proposal.target_user_id):
        await message.reply(FAM["not_your_button"])
        return

    if proposal.stage not in ("offer", "awaiting"):
        await message.reply(FAM["toast_stale"])
        return

    await message.reply(
        FAM["pm_vote"],
        reply_markup=_kb(proposal, initiator, target, _username(bot))
    )

@router.message(F.text.lower() == "браки", GroupOnlyFilter())
@inject
async def families_cmd(
    message: Message,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    families = await family_service.families_in_chat(message.chat.id)

    if not families:
        await message.reply(FAM["list_empty"])
        return

    rows = []

    for i, fam in enumerate(families, start=1):
        members = []

        for m in await family_service.family_repo.list_members(fam.id):
            u = await user_repo.get_by_id(m.user_id)

            if u is not None:
                members.append(_mention(u))

        names = ", ".join(members) if members else "—"

        if fam.name:
            rows.append(FAM["list_named"].format(place=i, name=html.escape(fam.name), members=names))
        else:
            rows.append(FAM["list_row"].format(place=i, members=names))

        await message.reply(FAM["list"].format(count=len(families), rows="\n".join(rows)))

@router.message(F.text.lower() == "развод", GroupOnlyFilter())
@router.message(F.text.lower() == "развестись", GroupOnlyFilter())
@inject
async def divorce_cmd(
    message: Message,
    user: UserData,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    me = await user_repo.get(user.telegram_id)

    if me is None or await family_service.family_repo.family_id_of(me.id) is None:
        await message.reply(FAM["single"])
        return

    await message.reply(FAM["divorce"]["ask"], reply_markup=divorce_kb(user.telegram_id))

@router.callback_query(F.data.startswith("fam_div_"), OwnerCallbackFilter())
@inject
async def divorce_cb(
    callback: CallbackQuery,
    user: UserData,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    me = await user_repo.get(user.telegram_id)

    if me is None:
        await callback.answer(FAM["toast_stale"], show_alert=False)
        return

    try:
        result = await family_service.divorce(me.id)
    except FamilyError:
        await callback.answer(FAM["divorce"]["stale"], show_alert=False)
        return

    heir = await user_repo.get_by_id(result.heir_id) if result.heir_id else None

    text = FAM["divorce"]["done"].format(
        name=_mention(me),
        heir=_mention(heir) if heir else "—",
        amount=format_num(result.inherited),
    )

    await _edit(callback.message, text)
    await callback.answer(show_alert=False)