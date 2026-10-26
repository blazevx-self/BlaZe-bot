from html import escape

from typing import Any, Callable, Dict, Awaitable
from datetime import datetime, UTC

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message

from dependency_injector.wiring import Provide

from app.containers import Container
from app.database.repositories.common.user import UserRepository

from app.utils.time import format_duration

class BanMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
            user_repo: UserRepository = Provide[Container.user_repo]
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        else:
            return await handler(event, data)

        user = await user_repo.get(user_id)

        if not user or not user.is_banned:
            return await handler(event, data)

        if user.banned_until is None:
            reason = user.ban_reason or "Не указана"

            text = (
                "<tg-emoji emoji-id=\"5258318620722733379\">🚫</tg-emoji> "
                f"<b>Вы заблокированы навсегда.</b>\n\n"
                "<tg-emoji emoji-id=\"5778299625370817409\">📝</tg-emoji> "
                f"<b>Причина:</b> "
                f"<i>{escape(reason)}</i>"
            )

            alert = (
                f"🚫 Вы заблокированы навсегда.\n\n"
                f"📝 Причина: {reason}"
            )

            if isinstance(event, Message):
                text_value = event.text or ""
                is_command = text_value.startswith("/")

                if is_command:
                    await event.reply(text)

            elif isinstance(event, CallbackQuery):
                await event.answer(alert, show_alert=True)

            return None

        now = datetime.now(UTC)

        if now >= user.banned_until:
            await user_repo.unban(telegram_id=user.telegram_id)
            return await handler(event, data)

        remaining_seconds = int((user.banned_until - now).total_seconds())

        duration = format_duration(
            remaining_seconds,
            show_seconds=remaining_seconds < 60
        )

        reason = user.ban_reason or "Не указана"

        text = (
            "<tg-emoji emoji-id=\"5258318620722733379\">🚫</tg-emoji> "
            f"<b>Вы заблокированы.</b>\n\n"
            "<tg-emoji emoji-id=\"5778299625370817409\">📝</tg-emoji> "
            f"<b>Причина:</b> "
            f"<i>{escape(reason)}</i>\n\n"
            "<tg-emoji emoji-id=\"5258258882022612173\">⏲️</tg-emoji> "
            f"До разблокировки: <b>{duration}</b>"
        )

        alert = (
            f"🚫 Вы заблокированы.\n\n"
            f"📝 Причина: {reason}\n\n"
            f"⏲️ До разблокировки: {duration}"
        )

        if isinstance(event, Message):
            text_value = event.text or ""
            is_command = text_value.startswith("/")

            if is_command:
                await event.reply(text)

        elif isinstance(event, CallbackQuery):
            await event.answer(alert, show_alert=True)

        return None