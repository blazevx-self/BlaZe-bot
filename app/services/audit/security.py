from app.core.constants.input.callbacks import ALLOWED_CALLBACK_PREFIXES
from app.core.constants.system.limits import (
    MAX_CALLBACK_LENGTH,
    SLOW_REQUEST_MS
)

from app.utils.logger import security_logger

class SecurityService:
    """
    Сервис проверки подозрительной активности пользователя.

    Отвечает за:
    - длину callback'ов
    - невалидные callback-префиксы
    - медленные запросы
    """

    @staticmethod
    def log_long_callback(user_info: str, callback_data: str) -> None:
        if len(callback_data) > MAX_CALLBACK_LENGTH:
            security_logger.warning(f"[SUSPICIOUS CALLBACK] {user_info} | callback={callback_data}")


    @staticmethod
    def log_invalid_callback(user_info: str, callback_data: str) -> None:
        """Проверяет callback на допустимые префиксы."""

        if not callback_data.startswith(ALLOWED_CALLBACK_PREFIXES):
            security_logger.warning(f"[INVALID CALLBACK] {user_info} | callback={callback_data}")


    @staticmethod
    def log_slow_request(
            user_info: str,
            process_time: float,
            event_name: str
    ) -> None:
        """Фиксирует медленные операции (performance monitoring)."""

        if process_time > SLOW_REQUEST_MS:
            security_logger.warning(f"[SLOW REQUEST] {user_info} | ping={process_time}ms | event={event_name}")

security_service = SecurityService()