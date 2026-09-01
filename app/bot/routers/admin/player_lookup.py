from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.user import UserNotFoundError

from app.services.admin.player_lookup_service import PlayerLookupService
from app.bot.filters.admin_filter import AdminFilter

router = Router()

@router.message(Command('admin_profile'), AdminFilter())
@inject
async def admin_profile_cmd(
    message: Message,
    player_lookup_service: PlayerLookupService = Provide[Container.player_lookup_service]
):
    if not message.text:
        return

    args = message.text.split(maxsplit=1)

    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_bot:
            await message.reply("⚠️ У ботов нет игрового профиля.")
            return

        query = str(message.reply_to_message.from_user.id)

    else:
        if len(args) < 2:
           await message.reply("<b>Использование:</b> /admin_profile «id или @username»")
           return

        query = args[1].strip()

    try:
        profile = await player_lookup_service.get_profile(query)
    except (UserNotFoundError, ValueError) as e:
        await message.reply(str(e))
        return

    await message.reply(player_lookup_service.fmt_profile_user(profile))