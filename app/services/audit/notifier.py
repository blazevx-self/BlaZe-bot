from html import escape
from typing import Any

from app.utils.logger import system_logger

class NotifierService:
    @staticmethod
    async def notify_admin(
        bot: Any,
        admin_ids: list[int],
        user_info: str,
        event_name: str,
        process_time: float,
        error: str,
        traceback_text: str
    ) -> None:
        error_text = (
            "<b>☕️ Кажется, мой тупой и криворукий разраб допустил ошибку.</b>\n\n"
            f"👤 <b>Ошибка была поймана у пользователя:</b> {escape(user_info)}\n"
            f"📦 <b>Событие:</b> {escape(event_name)}\n"
            f"⏱ <b>Время обработки:</b> {process_time}ms\n\n"
            f"<b>Ошибка:</b>\n"
            f"<code>{escape(error[:500])}</code>\n\n"
            f"<pre>{escape(traceback_text[-1500:])}</pre>"
        )

        for admin_id in admin_ids:
            try:
                await bot.send_message(admin_id, error_text)
            except Exception as e:
                system_logger.error(f"[NOTIFIER] Failed to send error to admin: {e}")

notifier_service = NotifierService()