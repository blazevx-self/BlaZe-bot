from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.user import UserNotFoundError

from app.services.admin.reset_service import ResetService
from app.bot.filters.admin_filter import AdminFilter

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
            await message.reply("⚠️ Нельзя удалить профиль бота.")
            return

        query = str(message.reply_to_message.from_user.id)

    else:
        if len(args) < 2:
            await message.reply("ℹ️ <b>Использование:</b> /reset_user «id или @username»")
            return

        query = args[1].strip()

    try:
        result = await reset_service.reset_user(query=query, admin_id=message.from_user.id)
    except (UserNotFoundError, ValueError) as e:
        await message.reply(str(e))
        return

    await message.reply(
        f"✅ Пользователь <code>{result.telegram_id}</code> "
        f"<b>полностью удалён.</b>\n\n"
        f"🧬 <b>Профиль гуля удалён:</b> "
        f"<code>{'да' if result.ghoul_deleted else 'не было'}</code>"
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
            await message.reply("⚠️ Нельзя удалить профиль бота.")
            return

        query = str(message.reply_to_message.from_user.id)

    else:
        if len(args) < 2:
            await message.reply("ℹ️ <b>Использование:</b> /reset_user «id или @username»")
            return

        query = args[1].strip()

    try:
        result = await reset_service.reset_ghoul(query=query, admin_id=message.from_user.id)
    except (UserNotFoundError, ValueError) as e:
        await message.reply(str(e))
        return

    await message.reply(
        f"✅ Профиль гуля пользователя "
        f"<code>{result.telegram_id}</code> <b>удалён.</b>"
    )