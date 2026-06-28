from app.utils.logger import (
    bot_logger,
    callback_logger,
    error_logger
)

class LoggerService:
    @staticmethod
    def log_message(
            user_info: str,
            chat_type: str,
            command: str,
            process_time: float
    ) -> None:
        bot_logger.info(f"[TEXT COMMAND] {user_info} | chat={chat_type} | command=\"{command}\" | ping={process_time:.2f}ms")

    @staticmethod
    def log_callback(
            user_info: str,
            callback_data: str,
            process_time: float
    ) -> None:
        callback_logger.info(f"[CALLBACK] {user_info} | callback=\"{callback_data}\" | ping={process_time:.2f}ms")

    @staticmethod
    def log_error(
            user_info: str,
            event_name: str,
            process_time: float,
            error: Exception
    ) -> None:
        error_logger.exception(f"[ERROR] {user_info} | event=\"{event_name}\" | ping={process_time:.2f}ms | error={error}")

logger_service = LoggerService()
