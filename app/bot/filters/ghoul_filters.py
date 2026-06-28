from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from app.utils.logger import security_logger

from app.services.ghoul_service import ghoul_service
from app.configs.yaml import cfg

class GhoulRequired(BaseFilter):
    async def __call__(
            self, event: Message | CallbackQuery,
            **kwargs
    ) -> bool:
        if not event.from_user:
            return False

        user = kwargs.get('user')
        is_ghoul = await ghoul_service.check_ghoul(event.from_user.id, cached_user=user)

        if is_ghoul:
            return True

        security_logger.warning(f"[GHOUL ACCESS DENIED] user_id: {event.from_user.id} | event: {event.__class__.__name__}")

        if isinstance(event, Message):
            await event.reply(cfg['message']['not_ghoul']['not_ghoul_message'], parse_mode="HTML")
        elif isinstance(event, CallbackQuery):
            await event.answer(cfg['message']['not_ghoul']['not_ghoul_callback'], show_alert=False)

        return False

