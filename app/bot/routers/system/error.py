from aiogram import Router
from aiogram.types import Message, CallbackQuery, ErrorEvent

from app.utils.logger import error_logger

router = Router()

@router.error()
async def global_rror(event: ErrorEvent) -> None:
    error_logger.exception(f"[ERROR HANDLER] {event.exception}")

    update = event.update
    if isinstance(update.message, Message):
        await update.message.answer(
            "<tg-emoji emoji-id=\"5386470514871003633\">☕️</tg-emoji> "
            "<b>Кажется, мой тупой криворукий разраб опять что-то сломал.</b>\n\n"
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            "<i>Ошибка уже отправлена ему автоматически.</i> "
            "<i>Попробуйте повторить действие немного позже.</i>"
        )

    elif isinstance(update.callback_query, CallbackQuery):
        await update.callback_query.answer(
            "☕ Что-то пошло не так.\n\n"
            "ℹ️ Ошибка уже отправлена разработчику. "
            "Попробуйте повторить действие немного позже",
            show_alert=True
        )