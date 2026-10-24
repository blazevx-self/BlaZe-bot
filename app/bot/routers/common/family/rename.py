import html

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from dependency_injector.wiring import Provide, inject

from app.containers import Container
from app.core.exceptions.chat import FamilyError

from app.types.entities.user import UserData

from app.database.repositories.common.user import UserRepository
from app.services.common.family import FamilyService

from app.bot.keyboards.common.family import rename_kb
from app.bot.filters.group_only import GroupOnlyFilter
from app.bot.filters.owner import OwnerCallbackFilter

from .helpers import FAM, _edit, _mention, _other_id, _username

router = Router()

@router.message(
    F.text.func(lambda t: bool(t) and t.lower().startswith("имя семьи")),
    GroupOnlyFilter(),
)
@inject
async def rename_cmd(
    message: Message,
    user: UserData,
    bot: Bot,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    parts = (message.text or "").split(maxsplit=2)

    if len(parts) < 3:
        await message.reply(FAM["rename"]["usage"])
        return

    me = await user_repo.get(user.telegram_id)

    if me is None:
        await message.reply(FAM["not_found"])
        return

    try:
        rename = await family_service.propose_rename(me.id, parts[2], message.chat.id)
    except FamilyError as e:
        await message.reply(str(e))
        return

    members = await family_service.family_repo.list_members(rename.family_id)

    other_id = _other_id(members, me.id)
    other = await user_repo.get_by_id(other_id) if other_id else None

    if other is None:
        await message.reply(FAM["not_found"])
        return

    sent = await message.reply(
        FAM["rename"]["ask"].format(
            initiator=_mention(me),
            name=html.escape(rename.name),
        ),
        reply_markup=rename_kb(rename.id, other.telegram_id, _username(bot)),
    )

    await family_service.set_rename_message_id(rename.id, sent.message_id)

@router.callback_query(F.data.startswith("fam_rn_ok_"), OwnerCallbackFilter())
@router.callback_query(F.data.startswith("fam_rn_no_"), OwnerCallbackFilter())
@inject
async def rename_answer_cb(
    callback: CallbackQuery,
    user: UserData,
    bot: Bot,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    parts = callback.data.split("_")
    agree = parts[2] == "ok"
    rename_id = int(parts[3])

    me = await user_repo.get(user.telegram_id)

    if me is None:
        await callback.answer(FAM["toast_stale"], show_alert=False)
        return

    try:
        rename = await family_service.answer_rename(rename_id, me.id, agree)
    except FamilyError as e:
        err = str(e)
        toast = FAM["toast_stale"] if ("актуально" in err or "истекло" in err) else None

        await callback.answer(toast, show_alert=False)
        return

    if agree:
        text = FAM["rename"]["done"].format(name=html.escape(rename.name))
        toast = FAM["toast_ok"]
    else:
        text = FAM["rename"]["declined"].format(name=_mention(me))
        toast = FAM["toast_declined"]

    if not isinstance(callback.message, Message):
        await callback.answer(FAM["toast_stale"], show_alert=False)
        return

    await _edit(callback.message, text)

    origin = callback.message

    if rename.message_id and (
        origin.chat.id != rename.chat_id
        or origin.message_id != rename.message_id
    ):
        try:
            await bot.edit_message_text(
                chat_id=rename.chat_id,
                message_id=rename.message_id,
                text=text,
            )
        except TelegramBadRequest:
            pass

    await callback.answer(toast, show_alert=False)