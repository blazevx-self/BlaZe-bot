import time

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from cachetools import TTLCache
from typing import Any, Callable, Dict, Awaitable

from app.utils.logger import security_logger

class AntifloodMiddleware(BaseMiddleware):
    """Middleware защиты от флуда.

    Ограничивает количество запросов пользователя за заданный интервал времени.
    """

    def __init__(
            self,
            limit_seconds: int = 5,
            max_requests: int = 15
    ):
        # user_id -> [timestamps]
        # TTLCache автоматически очищает пользователей после limit_seconds
        self.user_requests = TTLCache(maxsize=10_000, ttl=limit_seconds)
        self.limit_seconds = limit_seconds
        self.max_requests = max_requests

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """Контролирует частоту входящих событий пользователя."""

        from_user = getattr(event, 'from_user', None)

        if not from_user:
            return await handler(event, data)

        user_id = from_user.id
        now = time.monotonic()

        # Получаем историю запросов пользователя за ttl-окно
        requests = self.user_requests.get(user_id, [])

        # Оставляем только актуальные запросы внутри limit_seconds
        requests = [
            t for t in requests
            if now - t < self.limit_seconds
        ]

        requests.append(now)

        self.user_requests[user_id] = requests

        if len(requests) > self.max_requests:
            security_logger.warning(
                f"[FLOOD] User blocked | user_id={user_id} | "
                f"requests={len(requests)} | window={self.limit_seconds}s."
            )
            return None

        return await handler(event, data)


