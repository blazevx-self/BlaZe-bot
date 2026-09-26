from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.chat import ModerationError
from app.core.exceptions.user import UserNotFoundError

from app.services.chat.moderator.kick import ChatKickService
from app.bot.filters.group_only import GroupModeratorFilter

router = Router()

@router.message(Command("kick_chat"), GroupModeratorFilter())
@inject
async def kick_chat_cmd(
    message: Message,
    chat_kick_service: ChatKickService = Provide[Container.chat_kick_service]
):
    if not message.text or not message.from_user:
        return

    if message.reply_to_message and message.reply_to_message.from_user:
        args = message.text.split(maxsplit=1)

        if message.reply_to_message.from_user.is_bot:
            await message.reply(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя исключить бота."
            )
            return

        query = message.reply_to_message.from_user.id
        reason = args[1] if len(args) > 1 else None

    else:
        args = message.text.split(maxsplit=2)

        if len(args) < 2:
            await message.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Использование:</b> /kick_chat «id или @username» [причина]\n"
                "<b>Или ответом на сообщение:</b> /kick_chat [причина]"
            )
            return

        query = args[1]
        reason = args[2] if len(args) > 2 else None

    try:
        result = await chat_kick_service.kick(
            chat_id=message.chat.id,
            moderator_id=message.from_user.id,
            query=query,
            reason=reason,
        )
    except (UserNotFoundError, ModerationError) as e:
        await message.reply(str(e))
        return

    await message.reply(chat_kick_service.fmt_kick_result(result))