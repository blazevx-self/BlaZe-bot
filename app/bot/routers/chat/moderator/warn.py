from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.chat import ModerationError
from app.core.exceptions.user import UserNotFoundError

from app.services.chat.moderator.warn import ChatWarnService
from app.bot.filters.group_only import GroupModeratorFilter

router = Router()

@router.message(Command("warn_chat"), GroupModeratorFilter())
@inject
async def warn_chat_cmd(
    message: Message,
    chat_warn_service: ChatWarnService = Provide[Container.chat_warn_service]
):
    if not message.text or not message.from_user:
        return

    if message.reply_to_message and message.reply_to_message.from_user:
        args = message.text.split(maxsplit=1)

        if message.reply_to_message.from_user.is_bot:
            await message.reply(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя выдать предупреждение боту."
            )
            return

        query = message.reply_to_message.from_user.id
        reason = args[1] if len(args) > 1 else None

    else:
        args = message.text.split(maxsplit=2)

        if len(args) < 2:
            await message.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Использование:</b> /warn_chat «id или @username» [причина]\n"
                "<b>Или ответом на сообщение:</b> /warn_chat [причина]\n\n"
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "<b>Лимит:</b> <code>3 предупреждения</code>\n"
                "<b>После лимита</b> — <code>наказание выбирает модератор.</code>\n\n"
                "<tg-emoji emoji-id=\"5778299625370817409\">📝</tg-emoji> "
                "<b>Причина:</b> <code>текст</code>\n"
                "<b>Без неё — не указана.</b>"
            )
            return

        query = args[1]
        reason = args[2] if len(args) > 2 else None

    try:
        result = await chat_warn_service.warn(
            chat_id=message.chat.id,
            moderator_id=message.from_user.id,
            query=query,
            reason=reason,
        )
    except (UserNotFoundError, ModerationError) as e:
        await message.reply(str(e))
        return

    await message.reply(chat_warn_service.fmt_warn_result(result))

@router.message(Command("unwarn_chat"), GroupModeratorFilter())
@inject
async def unwarn_chat_cmd(
    message: Message,
    chat_warn_service: ChatWarnService = Provide[Container.chat_warn_service],
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
                "У ботов нет предупреждений."
            )
            return

        query = message.reply_to_message.from_user.id

    else:
        if len(args) < 2:
            await message.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Использование:</b> /unwarn_chat «id или @username»"
            )
            return

        query = args[1]

    try:
        result = await chat_warn_service.unwarn(
            chat_id=message.chat.id,
            moderator_id=message.from_user.id,
            query=query
        )
    except (UserNotFoundError, ModerationError) as e:
        await message.reply(str(e))
        return

    await message.reply(chat_warn_service.fmt_unwarn_result(result))