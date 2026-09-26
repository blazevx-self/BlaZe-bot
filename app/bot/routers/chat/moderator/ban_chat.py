from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.chat import ModerationError
from app.core.exceptions.user import UserNotFoundError

from app.services.chat.moderator.ban_chat import ChatBanService
from app.bot.filters.group_only import GroupModeratorFilter

router = Router()

@router.message(Command("ban_chat"), GroupModeratorFilter())
@inject
async def ban_chat_cmd(
    message: Message,
    chat_ban_service: ChatBanService = Provide[Container.chat_ban_service],
):
    if not message.text or not message.from_user:
       return

    if message.sender_chat:
        await message.reply(
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            "Отключи анонимность, чтобы использовать эту команду."
        )
        return

    if message.reply_to_message and message.reply_to_message.from_user:
        args = message.text.split(maxsplit=2)

        if message.reply_to_message.from_user.is_bot:
            await message.reply(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя заблокировать бота."
            )
            return

        query = message.reply_to_message.from_user.id
        duration = args[1] if len(args) > 1 else None
        reason = args[2] if len(args) > 2 else None

    else:
        args = message.text.split(maxsplit=3)

        if len(args) < 2:
            await message.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Использование:</b> /ban_chat «id или @username» [длительность] [причина]\n"
                "<b>Или ответом на сообщение:</b> /ban_chat [длительность] [причина]\n\n"
                "<tg-emoji emoji-id=\"5258258882022612173\">⏲️</tg-emoji> "
                "<b>Длительность:</b> <code>30m, 24h, 7d</code>\n"
                "<b>Без неё</b> — <code>навсегда.</code>\n\n"
                "<tg-emoji emoji-id=\"5778299625370817409\">📝</tg-emoji> "
                "<b>Причина:</b> <code>текст</code>\n"
                "<b>Без неё — не указана.</b>"
            )
            return

        query = args[1]
        duration = args[2] if len(args) > 2 else None
        reason = args[3] if len(args) > 3 else None

    try:
        result = await chat_ban_service.ban(
            chat_id=message.chat.id,
            moderator_id=message.from_user.id,
            query=query,
            duration=duration,
            reason=reason
        )
    except (UserNotFoundError, ModerationError) as e:
        await message.reply(str(e))
        return

    await message.reply(chat_ban_service.fmt_ban_result(result))

@router.message(Command("unban_chat"), GroupModeratorFilter())
@inject
async def unban_chat_cmd(
    message: Message,
    chat_ban_service: ChatBanService = Provide[Container.chat_ban_service],
):
    if not message.text or not message.from_user:
        return

    if message.sender_chat:
        await message.reply(
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            "Отключи анонимность, чтобы использовать эту команду."
        )
        return

    args = message.text.split(maxsplit=1)

    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_bot:
            await message.reply(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Ботов нельзя разблокировать."
            )
            return

        query = message.reply_to_message.from_user.id

    else:
        if len(args) < 2:
            await message.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Использование:</b> /unban_chat «id или @username»"
            )
            return

        query = args[1]

    try:
        result = await chat_ban_service.unban(
            chat_id=message.chat.id,
            moderator_id=message.from_user.id,
            query=query
        )
    except (UserNotFoundError, ModerationError) as e:
        await message.reply(str(e))
        return

    await message.reply(chat_ban_service.fmt_unban_result(result))