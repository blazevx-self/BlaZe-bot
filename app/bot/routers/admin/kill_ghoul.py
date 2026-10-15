from html import escape

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramForbiddenError

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.configs.yaml_loader import cfg

from app.core.exceptions.user import UserNotFoundError

from app.services.admin.kill_ghoul import KillGhoulService

from app.bot.keyboards.admin.kill_ghoul import get_kill_confirm_kb
from app.bot.filters.admin import AdminFilter

from app.utils.truncate_text import truncate_text

router = Router()

async def _get_query(message: Message) -> str | None:
    reply = message.reply_to_message

    if reply and reply.from_user:
        if reply.from_user.is_bot:
            await message.reply(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя убить бота."
            )
            return None
        return str(reply.from_user.id)

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.reply(
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            "<b>Использование:</b> /kill «id или @username»"
        )
        return None

    return args[1].strip()

@router.message(Command("kill_ghoul"), AdminFilter())
@inject
async def kill_cmd(
    message: Message,
    kill_ghoul_service: KillGhoulService = Provide[Container.kill_ghoul_service],
):
    query = await _get_query(message)

    if not query:
        return

    try:
        user = await kill_ghoul_service.resolve_user(query)
    except UserNotFoundError as e:
        await message.reply(str(e))
        return

    await message.reply(
        "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
        f"Убить пользователя <code>{user.telegram_id}</code> "
        f"({escape(truncate_text(user.name))})?\n\n"
        "<tg-emoji emoji-id=\"6028435952299413210\">ℹ️</tg-emoji> " 
        "Он сможет возродиться через <b>«растить кагуне».</b>",
        reply_markup=get_kill_confirm_kb(user.telegram_id),
    )

@router.callback_query(F.data.startswith("kill_confirm_"), AdminFilter())
@inject
async def kill_confirm(
    callback: CallbackQuery,
    bot: Bot,
    kill_ghoul_service: KillGhoulService = Provide[Container.kill_ghoul_service],
):
    target_id = int(callback.data.rsplit("_", 1)[1])

    try:
        result = await kill_ghoul_service.kill(query=target_id, admin_id=callback.from_user.id)
    except (UserNotFoundError, ValueError) as e:
        await callback.message.edit_text(str(e), reply_markup=None)
        await callback.answer()
        return

    await callback.message.edit_text(kill_ghoul_service.fmt_result(result), reply_markup=None)
    await callback.answer()

    if not result.already_dead:
        try:
            await bot.send_message(
                target_id,
                cfg["message"]["death"]["notify"]["admin"],
            )
        except TelegramForbiddenError:
            pass

@router.callback_query(F.data == "kill_cancel", AdminFilter())
async def kill_cancel(callback: CallbackQuery):
    await callback.message.edit_text(
        "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> "
        "<b>Убийство отменено.</b>",
        reply_markup=None,
    )
    await callback.answer()