from typing import Any

class NotifierService:
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

        error_text = (
            f"🚨 ERROR\n\n"
            f"👤 User: {user_info}\n"
            f"📦 Event: {event_name}\n"
            f"⏱ Time: {process_time}ms\n\n"
            f"💥 Error:\n"
            f"{error}\n\n"
            f"{traceback_text[-1500:]}"
        )

        await bot.send_message(admin_id, error_text)

notifier_service = NotifierService()