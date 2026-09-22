from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.configs.settings import settings

class AdminFilter(BaseFilter):
    """Проверяет, является ли отправитель владельцем бота."""

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in settings.ADMIN_IDS