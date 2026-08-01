import asyncio

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.types.entities import UserData
from app.utils.logger import system_logger

from app.database.repositories.users_repository import user_repository

class UserSyncMiddleware(BaseMiddleware):
    """Middleware синхронизации пользователя.

    Загружает пользователя из базы данных, создаёт нового
    при первом обращении и обновляет изменённые данные Telegram.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """Подготавливает объект пользователя и передаёт его в handler."""

        tg_user = data.get('event_from_user')

        if not tg_user:
            return await handler(event, data)

        try:
            raw_user_data = await user_repository.get_user_by_id(tg_user.id)

            if not raw_user_data:
                await self._create_user(tg_user)
                user_data = self._build_new_user(tg_user)

            else:
                user_data = await self._sync_user_data(tg_user, raw_user_data)

            data['user'] = user_data

        except Exception:
            system_logger.exception(f"[DB] Middleware failed | user_id={tg_user.id}")
            raise

        return await handler(event, data)


    @staticmethod
    async def _create_user(tg_user) -> None:
        """Создаёт нового пользователя."""

        try:
            await user_repository.create_user(
                user_id=tg_user.id,
                name=tg_user.first_name,
                username=tg_user.username,
            )
            system_logger.info(f"[DB] User created | user_id={tg_user.id}")

        except Exception:
            system_logger.exception(f"[DB] User created failed | user_id={tg_user.id}")
            raise


    async def _sync_user_data(self, tg_user, user_data: UserData) -> UserData:
        """Синхронизирует данные юзера с Telegram."""

        db_name = user_data.name
        db_username = user_data.username

        # Если имя изменено - обновляем в фоне БД, не тормозя хендлер
        if db_name != tg_user.first_name or db_username != tg_user.username:
            asyncio.create_task(
                self._update_user_data_safe(
                    user_id=tg_user.id,
                    name=tg_user.first_name,
                    username=tg_user.username
                )
            )

            user_data.name = tg_user.first_name
            user_data.username = tg_user.username

        return user_data


    @staticmethod
    async def _update_user_data_safe(
        user_id: int,
        name: str,
        username: str
    ) -> None:
        """Обновляет данные пользователя в фоне."""

        try:
            await user_repository.update_user_data(
                user_id=user_id,
                name=name,
                username=username
            )

            system_logger.info(f"[DB] User update | user_id={user_id}")

        except Exception:
            system_logger.exception(f"[DB] User update failed | user_id={user_id}")


    @staticmethod
    def _build_new_user(tg_user) -> UserData:
        """Собирает дефолтные данные нового юзера."""
        return UserData(
            user_id=tg_user.id,
            name=tg_user.first_name,
            username=tg_user.username,
            kagune_was_obtained=False,
        )