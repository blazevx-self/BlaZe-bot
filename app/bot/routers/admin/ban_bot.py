from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.user import UserNotFoundError

from app.services.admin.ban_bot import BanService
from app.bot.filters.admin import AdminFilter

router = Router()

@router.message(Command("ban_bot"), AdminFilter())
@inject
async def ban_bot(
    message: Message, ban_service: BanService = Provide[Container.ban_service]
):
    if not message.text:
        return

    if message.reply_to_message and message.reply_to_message.from_user:
        args = message.text.split(maxsplit=2)

        if message.reply_to_message.from_user.is_bot:
            await message.reply(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя заблокировать бота."
            )
            return

        query = str(message.reply_to_message.from_user.id)
        duration = args[1] if len(args) > 1 else None
        reason = args[2] if len(args) > 2 else None

    else:
        args = message.text.split(maxsplit=3)

        if len(args) < 2:
            await message.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Использование:</b> /ban_bot «id или @username» [длительность] [причина]\n\n"
                "<tg-emoji emoji-id=\"5258258882022612173\">⏲️</tg-emoji> "
                "<b>Длительность:</b> <code>30m, 24h, 7d</code>\n"
                "<b>Без неё</b> — <code>навсегда.</code>\n\n"
                "<tg-emoji emoji-id=\"5778299625370817409\">📝</tg-emoji> "
                "<b>Причина:</b> <code>текст</code>\n"
                "<b>Без нёё — не указана.</b>" 
            )
            return

        query = args[1]
        duration = args[2] if len(args) > 2 else None
        reason = args[3] if len(args) > 3 else None

    try:
        result = await ban_service.ban(
            query=query,
            duration=duration,
            reason=reason,
            admin_id=message.from_user.id
        )

    except (UserNotFoundError, ValueError) as e:
        await message.reply(text=str(e))
        return

    await message.reply(ban_service.fmt_ban_result(result))

@router.message(Command("unban_bot"), AdminFilter())
@inject
async def unban_user(
    message: Message, ban_service: BanService = Provide[Container.ban_service]
):
    if not message.text:
        return

    args = message.text.split(maxsplit=1)

    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_bot:
            await message.reply(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Ботов нельзя разблокировать."
            )
            return

        query = str(message.reply_to_message.from_user.id)

    else:
        if len(args) < 2:
            await message.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Использование:</b> /unban «id или @username»"
            )
            return

        query = args[1]

    try:
        user = await ban_service.unban(query)
    except (UserNotFoundError, ValueError) as e:
        await message.answer(text=str(e))
        return

    await message.answer(ban_service.fmt_unban_result(user)) 