from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from app.configs.yaml import cfg
from app.services.ghouls.ghoul_service import GhoulService

class GhoulRequired(BaseFilter):
    """Фильтр доступа.

    Разрешает выполнение обработчика только пользователем,
    получившим кагуне."""

    def __init__(self, ghoul_service: GhoulService):
        self.ghoul_service = ghoul_service

    async def __call__(
            self,
            event: Message | CallbackQuery,
            **kwargs
    ) -> bool:
        """Проверяет, является ли пользователь гулем."""

        if not event.from_user:
            return False

        ghoul = kwargs.get('ghoul')
        is_ghoul = await self.ghoul_service.check_ghoul(user_id=event.from_user.id, cached_ghoul=ghoul)

        if is_ghoul:
            return True

        if isinstance(event, Message):
            await event.reply(cfg['message']['not_ghoul']['not_ghoul_message'])

        elif isinstance(event, CallbackQuery):
            await event.answer(cfg['message']['not_ghoul']['not_ghoul_callback'], show_alert=False)

        return False