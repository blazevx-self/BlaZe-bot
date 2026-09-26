from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.enums import ChatType

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.common.user import UserRepository
from app.database.repositories.ghoul import GhoulRepository
from app.database.repositories.chat.chat import ChatRepository
from app.database.repositories.chat.chat_member import ChatMemberRepository

from app.database.mappers.user import orm_to_user
from app.database.mappers.ghoul import orm_to_ghoul

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
        tg_chat = data.get('event_chat')

        if not tg_user or tg_user.is_bot:
            return None

        is_private = bool(tg_chat and tg_chat.type == ChatType.PRIVATE)

        session: AsyncSession = data['session']

        try:
            user_repo = UserRepository(session)
            ghoul_repo = GhoulRepository(session)

            chat_repo = ChatRepository(session)
            chat_member_repo = ChatMemberRepository(session)
               
            user_orm = await user_repo.upsert(
                telegram_id=tg_user.id,
                name=tg_user.first_name,
                username=tg_user.username,
                has_private_chat=is_private
            )

            if tg_chat and tg_chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
                chat_orm = await chat_repo.upsert(
                    telegram_id=tg_chat.id,
                    title=tg_chat.title,
                    username=tg_chat.username,
                )

                await chat_member_repo.upsert(
                    chat_id=chat_orm.id,
                    user_id=user_orm.id,
                )

            ghoul_orm = await ghoul_repo.get(telegram_id=tg_user.id)
            
            data['user'] = orm_to_user(user_orm)
            data['ghoul'] = (orm_to_ghoul(ghoul_orm) if ghoul_orm else None)

        except Exception:
            database_logger.exception(f"[DB] Entity sync failed | id={tg_user.id}")
            raise
        
        return await handler(event, data)