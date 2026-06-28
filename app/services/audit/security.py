from app.core.constants.telegram import ALLOWED_CALLBACK_PREFIXES
from app.core.constants.audit import (
    MAX_MESSAGE_LENGTH,
    MAX_CALLBACK_LENGTH,
    SLOW_REQUEST_MS,
)

from app.utils.logger import security_logger

class SecurityService:
    @staticmethod
    def log_long_message(user_info: str, text: str) -> None:
        if len(text) > MAX_MESSAGE_LENGTH:
             security_logger.warning(f"[SUSPICIOUS MESSAGE] {user_info} | length={len(text)} chars")

    @staticmethod
    def log_long_callback(user_info: str, callback_data: str) -> None:
        if len(callback_data) > MAX_CALLBACK_LENGTH:
            security_logger.warning(f"[SUSPICIOUS CALLBACK] {user_info} | callback={callback_data}")

    @staticmethod
    def log_invalid_callback(user_info: str, callback_data: str) -> None:
        if not callback_data.startswith(ALLOWED_CALLBACK_PREFIXES):
            security_logger.warning(f"[INVALID CALLBACK] {user_info} | callback={callback_data}")

    @staticmethod
    def log_slow_request(
            user_info: str,
            process_time: float,
            event_name: str
    ) -> None:
        if process_time > SLOW_REQUEST_MS:
            security_logger.warning(f"[SLOW REQUEST] {user_info} | ping={process_time}ms | event={event_name}")

security_service = SecurityService()