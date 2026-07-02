from typing import Any

class NotifierService:
    """
    Сервис уведомления администратора о критических ошибках.

    Отправляет подробный отчёт в Telegram админа:
    - пользователь
    - событие
    - время выполнения
    - ошибка и traceback
    """

    @staticmethod
    async def notify_admin(
        bot: Any,
        admin_id: int,
        user_info: str,
        event_name: str,
        process_time: float,
        error: str,
        traceback_text: str
    ) -> None:
        """
        Отправляет уведомление администратору при возникновении ошибки.

        Используется для:
        - мониторинга боевых ошибок
        - быстрого реагирования на падения бота
        """

        error_text = (
            f"🚨 ERROR\n\n"
            f"👤 User: {user_info}\n"
            f"📦 Event: {event_name}\n"
            f"⏱ Time: {process_time}ms\n\n"
            f"Error:\n"
            f"{error}\n\n"
            f"{traceback_text[-1500:]}"
        )

        await bot.send_message(admin_id, error_text)

notifier_service = NotifierService()