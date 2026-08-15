from typing import Any, Callable, Dict, Awaitable
from datetime import timezone, datetime

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message

from app.database.repositories.users_repository import user_repository

class BanMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        else:
            return await handler(event, data)

        user = await user_repository.get_user_by_id(user_id)

        if not user:
            return await handler(event, data)

        if not user.is_banned:
            return await handler(event, data)

        if user.banned_until:
            banned_until = datetime.fromisoformat(user.banned_until)

            if datetime.now(timezone.utc) >= banned_until:
                await user_repository.unban(user_id)
                return await handler(event, data)

        text = f"🚫 <b>Вы заблокированы.</b>\n\n<b>Причина:</b> <i>{user.ban_reason or 'Не указана'}</i>"

        if isinstance(event, Message):
            await event.reply(text)

        elif isinstance(event, CallbackQuery):
            await event.answer(text, show_alert=True)

        return None 