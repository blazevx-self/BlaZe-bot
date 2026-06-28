import asyncio

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.database.repositories.users_repository import user_repository
from app.utils.logger import system_logger

class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:

        tg_user = data.get('event_from_user')

        if not tg_user:
            return await handler(event, data)

        raw_user_data = await user_repository.get_user_by_id(tg_user.id)

        if not raw_user_data:
            await user_repository.create_user(
                user_id=tg_user.id,
                name=tg_user.first_name,
                username=tg_user.username,
            )

            system_logger.info(f"[USER CREATED] id={tg_user.id}")

            # Чтобы не делать get_user_by... второй раз, собираем деф пак в память
            user_data = {
                'user_id': tg_user.id,
                'name': tg_user.first_name,
                'username': tg_user.username,
                'kagune_was_obtained': 0
            }
        else:
            user_data = dict(raw_user_data)
            db_name = user_data.get('name')
            db_username = user_data.get('username')

            # Если имя изменено - обновляем в фоне БД, не тормозя хендлер
            if db_name != tg_user.first_name or db_username != tg_user.username:
                asyncio.create_task(user_repository.update_user_data(
                    user_id=tg_user.id,
                    name=tg_user.first_name,
                    username=tg_user.username
                ))

                name_changed = db_name != tg_user.first_name
                username_changed = db_username != tg_user.username

                system_logger.info(
                    f"[USER UPDATED] id={tg_user.id} | "
                    f"name_changed={name_changed} | username_changed={username_changed}"
                )

                user_data['name'] = tg_user.first_name
                user_data['username'] = tg_user.username

        data['user'] = user_data
        return await handler(event, data)