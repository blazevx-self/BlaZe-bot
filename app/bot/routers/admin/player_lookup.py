from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.user import UserNotFoundError

from app.services.admin.player_lookup import PlayerLookupService
from app.bot.filters.admin import AdminFilter

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
            await message.reply(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                " У ботов нет игрового профиля."
            )
            return

        query = str(message.reply_to_message.from_user.id)

    else:
        if len(args) < 2:
           await message.reply(
               "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
               "<b>Использование:</b> /admin_profile «id или @username»"
           )
           return

        query = args[1].strip()

    try:
        profile = await player_lookup_service.get_profile(query)
    except (UserNotFoundError, ValueError) as e:
        await message.reply(text=str(e))
        return

    await message.reply(player_lookup_service.fmt_profile_user(profile))