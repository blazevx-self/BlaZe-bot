from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

class OwnerCallbackFilter(BaseFilter):
    """Проверяет, принадлежит та или иная кнопка пользователю.

    Если кнопка не его, бот ответит уведомлением, что это не его кнопка"""

    async def __call__(self, callback: CallbackQuery) -> bool:
        if not callback.data:
            return False

        try:
            owner_id = int(callback.data.rsplit("_", 1)[1])
        except (IndexError, ValueError):
            return False

        if callback.from_user.id != owner_id:
            await callback.answer(text="❌ Это не твоя кнопка", show_alert=False)
            return False

        return True