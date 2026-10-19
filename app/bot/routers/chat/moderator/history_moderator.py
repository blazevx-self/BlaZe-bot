from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from dependency_injector.wiring import inject, Provide

from app.containers import Container

from app.core.constants.chat.history_moderator import HISTORY_LIMIT
from app.core.exceptions.chat import ModerationError
from app.core.exceptions.user import UserNotFoundError

from app.services.chat.moderator.history_moderator import ChatHistoryService

from app.bot.filters.group_only import GroupOnlyFilter, GroupModeratorFilter
from app.bot.filters.owner import OwnerCallbackFilter

from app.bot.keyboards.chat.history import get_history_kb

router = Router()

async def _send_history(
    chat_history_service: ChatHistoryService,
    chat_id: int,
    moderator_id: int,
    query: str | int,
    offset: int,
):
    result = await chat_history_service.history(
        chat_id=chat_id,
        moderator_id=moderator_id,
        query=query,
        offset=offset,
    )
    text = chat_history_service.fmt_history_result(result)
    kb = get_history_kb(
        user_id=result.user.telegram_id,
        offset=result.offset,
        has_next=result.has_next,
        limit=HISTORY_LIMIT,
    )
    return text, kb


@router.message(Command("history_moder"), GroupOnlyFilter(), GroupModeratorFilter())
@inject
async def history_cmd(
    message: Message,
    chat_history_service: ChatHistoryService = Provide[Container.chat_history_service],
):
    if not message.text or not message.from_user:
        return

    args = message.text.split(maxsplit=1)

    if message.reply_to_message and message.reply_to_message.from_user:
        query = message.reply_to_message.from_user.id
    elif len(args) > 1:
        query = args[1]
    else:
        await message.reply(
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            "<b>Использование:</b> /history_moder «id или @username»"
        )
        return

    try:
        text, kb = await _send_history(
            chat_history_service, message.chat.id, message.from_user.id, query, 0
        )
    except (UserNotFoundError, ModerationError) as e:
        await message.reply(str(e))
        return

    await message.reply(text, reply_markup=kb)


@router.callback_query(F.data.startswith("hist_"), OwnerCallbackFilter())
@inject
async def history_page(
    callback: CallbackQuery,
    chat_history_service: ChatHistoryService = Provide[Container.chat_history_service],
):
    if callback.message is None or not callback.from_user or not callback.data:
        await callback.answer()
        return

    try:
        _, user_id_s, offset_s = callback.data.split("_")
        user_id = int(user_id_s)
        offset = int(offset_s)
    except ValueError:
        await callback.answer()
        return

    try:
        text, kb = await _send_history(
            chat_history_service,
            chat_id=callback.message.chat.id,
            moderator_id=callback.from_user.id,
            query=user_id,
            offset=offset,
        )
    except (UserNotFoundError, ModerationError) as e:
        await callback.answer(str(e), show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(text, reply_markup=kb)