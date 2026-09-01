from typing import Any, Callable, Dict, Awaitable
from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message

from dependency_injector.wiring import Provide

from app.containers import Container
from app.database.repositories.users_repository import UserRepository

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

        if user.banned_until:
            if datetime.utcnow() >= user.banned_until:
                await user_repo.unban(telegram_id=user.telegram_id)
                return await handler(event, data)

        text = f"🚫 <b>Вы заблокированы.</b>\n\n<b>Причина:</b> <i>{user.ban_reason or 'Не указана'}</i>"

        if isinstance(event, Message):
            await event.reply(text)

        elif isinstance(event, CallbackQuery):
            await event.answer(text, show_alert=True)

        return None