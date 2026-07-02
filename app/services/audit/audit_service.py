from aiogram.types import Message, CallbackQuery
from typing import Any

from app.services.audit.logger import logger_service
from app.services.audit.notifier import notifier_service
from app.services.audit.security import security_service

from app.configs.yaml import cfg

class AuditService:
    """
    Центральный фасад аудита.

    Объединяет:
    - логирование действий (LoggerService)
    - security проверки (SecurityService)
    - уведомления админа (NotifierService)

    Используется в middleware для единой точки аудита событий.
    """

    @staticmethod
    def handle_message(
            user_info: str,
            message: Message,
            process_time: float
    ) -> None:
        """
        Обрабатывает входящее текстовое сообщение.

        Выполняет:
        - логирование команды
        - security проверки
        - фильтрацию системных сообщений
        - контроль производительности
        """

        text = message.text or "NOT TEXT"
        chat_type = message.chat.type

        if text.startswith("/"):
            return

        logger_service.log_message(
            user_info=user_info,
            chat_type=chat_type,
            command=text,
            process_time=process_time
        )

        security_service.log_slow_request(
            user_info=user_info,
            process_time=process_time,
            event_name=message.__class__.__name__
        )

    @staticmethod
    def handle_callback(
            user_info: str,
            callback: CallbackQuery,
            process_time: float
    ) -> None:
        """
        Обрабатывает callback-запрос.

        Выполняет:
        - логирование callback действий
        - security проверки
        - контроль скорости обработки
        """

        callback_data = callback.data or "NOT DATA"

        logger_service.log_callback(
            user_info=user_info,
            callback_data=callback_data,
            process_time=process_time
        )

        security_service.log_long_callback(
            user_info=user_info,
            callback_data=callback_data
        )

        security_service.log_invalid_callback(
            user_info=user_info,
            callback_data=callback_data
        )

        security_service.log_slow_request(
            user_info=user_info,
            process_time=process_time,
            event_name=callback.__class__.__name__
        )

    @staticmethod
    async def handle_exception(
            *,
            bot: Any,
            user_info: str,
            event_name: str,
            process_time: float,
            error: Exception,
            traceback_text: str
    ) -> None:
        """
        Обрабатывает исключения в middleware/хендлерах.

        Выполняет:
        - логирование ошибки
        - уведомление администратора
        """

        logger_service.log_error(
            user_info=user_info,
            event_name=event_name,
            process_time=process_time,
            error=error
        )

        admin_id = cfg['settings']['admin_id']

        if not bot or not admin_id:
            return

        try:
            await notifier_service.notify_admin(
                bot=bot,
                admin_id=admin_id,
                user_info=user_info,
                event_name=event_name,
                process_time=process_time,
                error=str(error),
                traceback_text=traceback_text
            )
        except Exception as notify_error:
            logger_service.log_error(
                user_info="SYSTEM",
                event_name="ADMIN NOTIFY FAILED",
                process_time=0,
                error=notify_error
            )

audit_service = AuditService()