from app.utils.logger import (
    bot_logger,
    callback_logger,
    error_logger
)


class LoggerService:
    """
        Сервис логирования пользовательских действий.

        Отвечает за:
        - логирование текстовых команд
        - логирование callback-запросов
        - логирование ошибок

        Использует разные логгеры (bot/callback/error) для разделения потоков логов.
    """

    @staticmethod
    def log_message(
            user_info: str,
            chat_type: str,
            command: str,
            process_time: float
    ) -> None:
        """
        Логирует текстовую команду пользователя.

        Форматирует:
        - пользователя
        - чат
        - текст команды
        - время обработки запроса
        """

        bot_logger.info(f"[TEXT COMMAND] {user_info} | chat={chat_type} | command=\"{command}\" | ping={process_time:.2f}ms")


    @staticmethod
    def log_callback(
            user_info: str,
            callback_data: str,
            process_time: float
    ) -> None:
        """
        Логирует callback-запрос (inline кнопки).

        Используется для отслеживания:
        - действий пользователя в UI
        - навигации по меню
        """

        callback_logger.info(f"[CALLBACK] {user_info} | callback=\"{callback_data}\" | ping={process_time:.2f}ms")


    @staticmethod
    def log_error(
            user_info: str,
            event_name: str,
            process_time: float,
    ) -> None:
        """
        Логирует исключения уровня ERROR.

        Используется для:
        - фиксации ошибок выполнения хендлеров
        - последующего анализа через error-лог
        """

        error_logger.exception(f"[ERROR] {user_info} | event=\"{event_name}\" | ping={process_time:.2f}ms")

logger_service = LoggerService()
