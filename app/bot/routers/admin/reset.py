from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.user import UserNotFoundError

from app.services.admin.reset import ResetService
from app.bot.filters.admin import AdminFilter

router = Router()

@router.message(Command('reset_user'), AdminFilter())
@inject
async def reset_user_cmd(
    message: Message, reset_service: ResetService = Provide[Container.reset_service]
):
    if not message.text:
        return

    args = message.text.split(maxsplit=1)

    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_bot:
            await message.reply(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя удалить профиль бота."
            )
            return

        query = str(message.reply_to_message.from_user.id)

    else:
        if len(args) < 2:
            await message.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Использование:</b> /reset_user «id или @username»"
            )
            return

        query = args[1].strip()

    try:
        result = await reset_service.reset_user(query=query, admin_id=message.from_user.id)
    except (UserNotFoundError, ValueError) as e:
        await message.reply(text=str(e))
        return

    await message.reply(
        "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
        f"Пользователь <code>{result.telegram_id}</code> "
        f"<b>полностью удалён.</b>\n\n"
        "<tg-emoji emoji-id=\"5260399854500191689\">👤</tg-emoji> "
        f"<b>Профиль гуля удалён:</b> "
        f"{'да' if result.ghoul_deleted else 'не было'}"
    )

@router.message(Command('reset_ghoul'), AdminFilter())
@inject
async def reset_ghoul_cmd(
    message: Message, reset_service: ResetService = Provide[Container.reset_service]
):
    if not message.text:
        return

    args = message.text.split(maxsplit=1)

    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_bot:
            await message.reply(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя удалить профиль бота."
            )
            return

        query = str(message.reply_to_message.from_user.id)

    else:
        if len(args) < 2:
            await message.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Использование:</b> /reset_user «id или @username»"
            )
            return

        query = args[1].strip()

    try:
        result = await reset_service.reset_ghoul(query=query, admin_id=message.from_user.id)
    except (UserNotFoundError, ValueError) as e:
        await message.reply(text=str(e))
        return

    await message.reply(
        "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
        f"Профиль гуля пользователя "
        f"<code>{result.telegram_id}</code> <b>удалён.</b>"
    )