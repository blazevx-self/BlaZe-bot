from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery

from typing import Any, Callable, Dict, Awaitable
from cachetools import TTLCache

from app.configs.yaml import cfg
from app.utils.logger import security_logger

class AntiSpamGhoulMiddleware(BaseMiddleware):
    """Middleware защиты от спама callback-кнопками.

    Блокирует слишком частые повторные нажатия
    в течение короткого промежутка времени.
    """

    def __init__(self, time_limit: float = 0.7) -> None:
        self.cache = TTLCache(maxsize=10_000, ttl=time_limit)

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
            """Проверяет частоту callback-запросов пользователя."""

            if isinstance(event, CallbackQuery):
                user_id = event.from_user.id
                callback = event.data or "unknown"

                # защита от повторных нажатий кнопок (callback spam)
                if user_id in self.cache:
                    security_logger.warning(
                        f"[SPAM] Callback blocked | "
                        f"user_id={user_id} | callback={callback[:50]}"
                    )

                    await event.answer(cfg['message']['middleware_text_antispam'], show_alert=False)
                    return None

                self.cache[user_id] = True

            return await handler(event, data)

