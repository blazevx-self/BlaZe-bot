import html

from aiogram import Bot, F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message

from dependency_injector.wiring import Provide, inject

from app.containers import Container
from app.core.constants.game.family import MARRIAGE_PRICE
from app.core.exceptions.chat import FamilyError

from app.types.entities.user import UserData

from app.database.repositories.common.user import UserRepository
from app.services.common.family import FamilyService

from app.bot.keyboards.common.family import offer_kb, rename_kb
from app.bot.filters.group_only import GroupOnlyFilter
from app.bot.filters.owner import OwnerCallbackFilter

from app.utils.format_num import format_num

from .helpers import (
    FAM, _edit, _invite, _kb,
    _mention, _pair, _sync_group,
    _username,
)

router = Router()

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
        await message.reply(FAM["usage"])
        return

    if reply.from_user.is_bot:
        await message.reply(FAM["bot"])
        return

    initiator = await user_repo.get(user.telegram_id)
    target = await user_repo.get(reply.from_user.id)

    if initiator is None or target is None:
        await message.reply(FAM["not_found"])
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

    if not isinstance(callback.message, Message):
        await callback.answer(FAM["toast_stale"], show_alert=False)
        return

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

    if not isinstance(callback.message, Message):
        await callback.answer(FAM["toast_stale"], show_alert=False)
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

    if not isinstance(callback.message, Message):
        await callback.answer(FAM["toast_stale"], show_alert=False)
        return

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

    if args.startswith("famrn_"):
        try:
            rename_id = int(args.removeprefix("famrn_"))
        except ValueError:
            return

        me = await user_repo.get(user.telegram_id)

        if me is None:
            return

        try:
            rename = await family_service.get_rename(rename_id)
        except FamilyError:
            await message.reply(FAM["toast_stale"])
            return

        if rename.stage != "awaiting":
            await message.reply(FAM["toast_stale"])
            return

        if me.id == rename.proposer_user_id:
            await message.reply(FAM["toast_wait"])
            return

        members = await family_service.family_repo.list_members(rename.family_id)

        if me.id not in {m.user_id for m in members}:
            await message.reply(FAM["not_your_button"])
            return

        await message.reply(
            FAM["rename"]["pm_vote"].format(name=html.escape(rename.name)),
            reply_markup=rename_kb(rename.id, user.telegram_id, _username(bot)),
        )
        return

    if not args.startswith("fam_"):
        return

    try:
        proposal_id = int(args.removeprefix("fam_"))
    except ValueError:
        return

    me = await user_repo.get(user.telegram_id)

    if me is None:
        return

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
        reply_markup=_kb(proposal, initiator, target, _username(bot)),
    )