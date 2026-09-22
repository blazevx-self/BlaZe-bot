import asyncio
from collections.abc import Callable, Awaitable

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)

from app.types.services_result.admin import BroadcastResult

from app.database.repositories.common.user import UserRepository
from app.database.repositories.chat import ChatRepository

from app.utils.logger import admin_logger

class BroadcastService:
    def __init__(
        self,
        user_repo: UserRepository,
        chat_repo: ChatRepository,
        bot: Bot
    ):
        self.user_repo = user_repo
        self.chat_repo = chat_repo
        self.bot = bot

    async def send_to_user(self, telegram_id: int, text: str) -> bool:
        try:
            await self.bot.send_message(chat_id=telegram_id, text=text)
            return True
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)

            try:
                await self.bot.send_message(chat_id=telegram_id, text=text)
                return True
            except Exception as e:
                admin_logger.warning(f"[BROADCAST] Retry failed | user_id={telegram_id}: {e}")
                return False

        except (TelegramForbiddenError, TelegramBadRequest) as e:
            admin_logger.warning(f"[BROADCAST] Cannot send | user_id={telegram_id}: {e}")
            return False

    async def send_to_chat(self, telegram_id: int, text: str) -> bool:
        try:
            await self.bot.send_message(chat_id=telegram_id, text=text)
            return True
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)

            try:
                await self.bot.send_message(chat_id=telegram_id, text=text)
                return True
            except Exception as e:
                admin_logger.warning(f"[BROADCAST] Retry failed | chat_id={telegram_id}: {e}")
                return False

        except (TelegramForbiddenError, TelegramBadRequest) as e:
            admin_logger.warning(f"[BROADCAST] Cannot send | chat_id={telegram_id}: {e}")
            return False

    async def broadcast_to_private(self, text: str) -> BroadcastResult:
        users = await self.user_repo.get_all_with_private_chat()
        target_ids = [u.telegram_id for u in users]

        return await self._broadcast(target_ids, text, self.send_to_user)

    async def broadcast_to_chats(self, text: str) -> BroadcastResult:
        chats = await self.chat_repo.get_all()
        target_ids = [c.telegram_id for c in chats]

        return await self._broadcast(target_ids, text, self.send_to_chat)

    async def broadcast_to_all(self, text: str) -> BroadcastResult:
        private_result = await self.broadcast_to_private(text)
        chats_result = await self.broadcast_to_chats(text)

        return BroadcastResult(
            total=private_result.total + chats_result.total,
            success=private_result.success + chats_result.success,
            failed=private_result.failed + chats_result.failed
        )

    async def send_to_target(self, query: str | int, text: str) -> bool:
        user = await self.user_repo.resolve(query)

        if not user:
            return False

        return await self.send_to_user(user.telegram_id, text)

    @staticmethod
    async def _broadcast(
        targets: list[int],
        text: str,
        sender: Callable[[int, str], Awaitable[bool]],
        progress_cb: Callable[[int, int, int, int], Awaitable[None]] | None = None
    ) -> BroadcastResult:
        success = 0
        failed = 0

        for i, target_id in enumerate(targets, start=1):
            ok = await sender(target_id, text)

            if ok:
                success += 1
            else:
                failed += 1

            if progress_cb and i % 25 == 0:
                await progress_cb(i, len(targets), success, failed)

            # flood control
            await asyncio.sleep(0.05)

        return BroadcastResult(
            total=len(targets),
            success=success,
            failed=failed
        )