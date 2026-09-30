from html import escape

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.user import UserNotFoundError

from app.services.admin.reset import ResetService

from app.bot.keyboards.admin.reset import get_reset_confirm_kb
from app.bot.filters.admin import AdminFilter

from app.utils.truncate_text import truncate_text

router = Router()

async def _get_query(message: Message, command: str) -> str | None:
    reply = message.reply_to_message

    if reply and reply.from_user:
        if reply.from_user.is_bot:
            await message.reply(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя удалить профиль бота."
            )
            return None

        return str(reply.from_user.id)

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.reply(
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            f"<b>Использование:</b> /{command} «id или @username»"
        )
        return None

    return args[1].strip()

async def _ask_confirm(
    message: Message,
    reset_service: ResetService,
    action: str,
    text: str
):
    query = await _get_query(message, f"reset_{action}")

    if not query:
        return

    try:
        user = await reset_service.resolve_user(query)
    except UserNotFoundError as e:
        await message.reply(str(e))
        return

    await message.reply(
        "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
        f"{text} <code>{user.telegram_id}</code> "
        f"({escape(truncate_text(user.name))})?\n\n"
        "<b>Это действие нельзя отменить.</b>",
        reply_markup=get_reset_confirm_kb(action=action, target_id=user.telegram_id)
    )

@router.message(Command('reset_user'), AdminFilter())
@inject
async def reset_user_cmd(
    message: Message,
    reset_service: ResetService = Provide[Container.reset_service]
):
    await _ask_confirm(message, reset_service, "user", "Полностью удалить пользователя")

@router.message(Command('reset_ghoul'), AdminFilter())
@inject
async def reset_ghoul_cmd(
    message: Message,
    reset_service: ResetService = Provide[Container.reset_service]
):
    await _ask_confirm(message, reset_service, "ghoul", "Удалить гуля пользователя")

@router.callback_query(F.data.startswith("reset_user_confirm_"), AdminFilter())
@inject
async def reset_user_confirm(
    callback: CallbackQuery,
    reset_service: ResetService = Provide[Container.reset_service]
):
    target_id = int(callback.data.rsplit("_", 1)[1])

    try:
        result = await reset_service.reset_user(query=target_id, admin_id=callback.from_user.id)
    except UserNotFoundError as e:
        await callback.message.edit_text(str(e), reply_markup=None)
        await callback.answer()
        return

    await callback.message.edit_text(
        "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
        f"Пользователь <code>{result.telegram_id}</code> "
        f"<b>полностью удалён.</b>\n\n"
        "<tg-emoji emoji-id=\"5260399854500191689\">👤</tg-emoji> "
        f"<b>Профиль гуля удалён:</b> "
        f"{'да' if result.ghoul_deleted else 'не было'}",
        reply_markup=None
    )
    await callback.answer()

@router.callback_query(F.data.startswith("reset_ghoul_confirm_"), AdminFilter())
@inject
async def reset_ghoul_confirm(
    callback: CallbackQuery,
    reset_service: ResetService = Provide[Container.reset_service]
):
    target_id = int(callback.data.rsplit("_", 1)[1])

    try:
        result = await reset_service.reset_ghoul(query=target_id, admin_id=callback.from_user.id)
    except UserNotFoundError as e:
        await callback.message.edit_text(str(e), reply_markup=None)
        await callback.answer()
        return

    text = (
        f"Профиль гуля пользователя <code>{result.telegram_id}</code> <b>удалён.</b>"
        if result.ghoul_deleted
        else f"У пользователя <code>{result.telegram_id}</code> <b>не было гуля.</b>"
    )

    await callback.message.edit_text(
        "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> " + text,
        reply_markup=None
    )
    await callback.answer()

@router.callback_query(F.data == "reset_cancel", AdminFilter())
async def reset_cancel(callback: CallbackQuery):
    await callback.message.edit_text(
        "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> "
        "<b>Удаление отменено.</b>",
        reply_markup=None
    )
    await callback.answer()