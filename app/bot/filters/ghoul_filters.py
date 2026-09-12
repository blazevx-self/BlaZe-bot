from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from dependency_injector.wiring import Provide

from app.configs.yaml_loader import cfg
from app.containers import Container

from app.services.ghouls.ghoul_service import GhoulService

class GhoulRequired(BaseFilter):
    """Фильтр доступа.

    Разрешает выполнение обработчика только пользователем,
    получившим кагуне."""

    async def __call__(
        self,
        event: Message | CallbackQuery,
        ghoul_service: GhoulService = Provide[Container.ghoul_service],
        **kwargs
    ) -> bool:
        """Проверяет, является ли пользователь гулем."""

        if not event.from_user:
            return False

        ghoul = kwargs.get("ghoul")
        is_ghoul = await ghoul_service.check_ghoul(user_id=event.from_user.id, cached_ghoul=ghoul)

        if is_ghoul:
            return True

        if isinstance(event, Message):
            await event.reply(cfg['message']['not_ghoul']['not_ghoul_message'])

        elif isinstance(event, CallbackQuery):
            await event.answer(cfg['message']['not_ghoul']['not_ghoul_callback'], show_alert=False)

        return False