from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.chat import ModerationError
from app.core.exceptions.user import UserNotFoundError

from app.services.chat.moderator.history_moderator import ChatHistoryService
from app.bot.filters.group_only import GroupModeratorFilter\

router = Router()

@router.message(Command('history_moder'), GroupModeratorFilter())
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
            "<b>Использование:</b> /history_moder «id или @username»\n\n"
            "<b>Или ответом на сообщение:</b> /history_moder"
        )
        return

    try:
        result = await chat_history_service.history(
            chat_id=message.chat.id,
            moderator_id=message.from_user.id,
            query=query
        )
    except (UserNotFoundError, ModerationError) as e:
        await message.reply(str(e))
        return

    await message.reply(chat_history_service.fmt_history_result(result))