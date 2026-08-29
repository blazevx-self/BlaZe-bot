from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.users_repository import UserRepository
from app.database.repositories.ghouls_repository import GhoulRepository

from app.database.mappers.user_mapper import orm_to_user
from app.database.mappers.ghoul_mapper import orm_to_ghoul

from app.utils.logger import database_logger

class SyncEntitiesMiddleware(BaseMiddleware):
    """Middleware синхронизации сущностей.

    Загружает пользователя и, если он уже гуль, его сущность."""

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        tg_user = data.get('event_from_user')

        if not tg_user or tg_user.is_bot:
            return None

        session: AsyncSession = data['session']

        try:
            user_repo = UserRepository(session)
            ghoul_repo = GhoulRepository(session)
               
            user_orm = await user_repo.upsert(
                telegram_id=tg_user.id,
                name=tg_user.first_name,
                username=tg_user.username
            )

            ghoul_orm = await ghoul_repo.get(telegram_id=tg_user.id)
            
            data['user'] = orm_to_user(user_orm)
            data['ghoul'] = (orm_to_ghoul(ghoul_orm) if ghoul_orm else None)

        except Exception:
            database_logger.exception(f"[DB] Entity sync failed | id={tg_user.id}")
            raise
        
        return await handler(event, data)