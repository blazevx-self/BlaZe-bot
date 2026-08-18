from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.services.admin.ban_service import ban_service
from app.bot.filters.admin_filter import AdminFilter

router = Router()

@router.message(Command("ban_bot"), AdminFilter())
async def ban_bot(message: Message):
    if not message.text:
        return

    args = message.text.split(maxsplit=2)

    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_bot:
            await message.reply("⚠️ Нельзя заблокировать бота.")
            return

        query = str(message.reply_to_message.from_user.id)
        duration = args[1] if len(args) > 1 else None
        reason = args[2] if len(args) > 2 else None

    else:
        if len(args) < 2:
            await message.reply(
                "<b>Использование:</b> /ban «id или @username» [длительность] [причина]\n\n"
                "<b>Длительность:</b> <code>30m, 24h, 7d</code>\n"
                "<b>Без неё</b> — <code>навсегда.</code>\n\n"
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
        )

    except ValueError as e:
        await message.reply(str(e))
        return

    await message.reply(ban_service.fmt_ban_result(result))


@router.message(Command("unban_bot"), AdminFilter())
async def unban_user(message: Message):
    if not message.text:
        return

    args = message.text.split(maxsplit=1)

    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_bot:
            await message.reply("⚠️ Ботов нельзя разблокировать.")
            return

        query = str(message.reply_to_message.from_user.id)

    else:
        if len(args) < 2:
            await message.reply("<b>Использование:</b> /unban «id или @username»")
            return

        query = args[1]

    try:
        user = await ban_service.unban(query)
    except ValueError as e:
        await message.answer(str(e))
        return

    await message.answer(ban_service.fmt_unban_result(user)) 