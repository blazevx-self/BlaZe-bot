import time
import traceback

from typing import Any, Callable, Awaitable, Dict
from aiogram.types import TelegramObject, CallbackQuery, Message
from aiogram import BaseMiddleware

from app.services.audit.audit_service import audit_service
from app.services.audit.formatters import build_user_info

class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования событий.

    Логирует входящие сообщения, callback-запросы,
    время обработки и необработанные исключения.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """Передаёт событие обработчику и выполняет аудит."""

        start_time = time.perf_counter()
        from_user = getattr(event, "from_user", None)

        try:
            result = await handler(event, data)
            process_time = round((time.perf_counter() - start_time) * 1000, 2)

            user_info = build_user_info(
                from_user=from_user,
                user_db=data.get("user")
            )

            if isinstance(event, Message):
                audit_service.handle_message(
                    user_info=user_info,
                    message=event,
                    process_time=process_time
                )

            elif isinstance(event, CallbackQuery):
                audit_service.handle_callback(
                    user_info=user_info,
                    callback=event,
                    process_time=process_time
                )

            return result

        except Exception as e:
            process_time = round((time.perf_counter() - start_time) * 1000, 2)

            user_info = build_user_info(
                    from_user=from_user,
                    user_db=data.get("user")
                )

            tb = traceback.format_exc()

            await audit_service.handle_exception(
                bot=data.get("bot"),
                user_info=user_info,
                event_name=event.__class__.__name__,
                process_time=process_time,
                error=e,
                traceback_text=tb
            )