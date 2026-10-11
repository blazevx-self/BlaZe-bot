import time

from collections import deque
from datetime import timedelta
from html import escape
from typing import Any, Awaitable, Callable, Dict

from cachetools import TTLCache

from aiogram import BaseMiddleware
from aiogram.types import Message, ChatPermissions
from aiogram.exceptions import TelegramAPIError

from app.core.constants.chat.chat_restrictions import GROUP_TYPES, MODERATOR_STATUSES

from app.utils.logger import security_logger
from app.utils.truncate_text import truncate_text

class AntiSpamForChatsMiddleware(BaseMiddleware):
    """
        Антиспам для групп: пачка сообщений -> предупреждение, N предупреждений -> мут.

        Всё считается в памяти. Мут выдаётся через Telegram (restrict), поэтому
        его не нужно проверять на каждом сообщении - Telegram сам не даст писать.
    """

    def __init__(
        self,
        max_messages: int = 5,
        window_seconds: int = 4,
        max_warnings: int = 3,
        warnings_ttl_minutes: int = 10,
        mute_minutes: int = 10,
    ) -> None:
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.max_warnings = max_warnings
        self.mute_duration = timedelta(minutes=mute_minutes)

        self._messages: TTLCache[tuple[int, int], deque[float]] = TTLCache(
            maxsize=50_000,
            ttl=window_seconds
        )

        self._warnings: TTLCache[tuple[int, int], int] = TTLCache(
            maxsize=50_000,
            ttl=warnings_ttl_minutes * 60
        )

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if (
            event.chat.type not in GROUP_TYPES
            or not event.from_user
            or event.from_user.is_bot
            or event.sender_chat
        ):
            return await handler(event, data)

        key = (event.chat.id, event.from_user.id)

        if not self._is_spam(key):
            return await handler(event, data)

        if await self._is_moderator(event):
            return await handler(event, data)

        await self._punish(event, key)

        return None

    def _is_spam(self, key: tuple[int, int]) -> bool:
        now = time.monotonic()

        timestamps = self._messages.get(key) or deque()
        timestamps.append(now)

        while now - timestamps[0] > self.window_seconds:
            timestamps.popleft()

        if len(timestamps) < self.max_messages:
            self._messages[key] = timestamps
            return False

        self._messages.pop(key, None)

        return True

    async def _punish(self, message: Message, key: tuple[int, int]) -> None:
        name = escape(truncate_text(message.from_user.first_name))
        warnings = self._warnings.get(key, 0) + 1

        if warnings < self.max_warnings:
            self._warnings[key] = warnings

            await self._reply(
                message,
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"<b>{name}</b>, сбавь темп. Предупреждение <b>{warnings}/{self.max_warnings}</b> за спам."
            )
            return

        self._warnings.pop(key, None)

        try:
            await message.bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=message.from_user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=self.mute_duration
            )
        except TelegramAPIError as e:
            security_logger.warning(f"[SPAM] Mute failed | chat_id={key[0]} | user_id={key[1]} | {e}")
            return

        security_logger.warning(f"[SPAM] Muted | chat_id={key[0]} | user_id={key[1]}")

        minutes = int(self.mute_duration.total_seconds() // 60)

        await self._reply(
            message,
            "<tg-emoji emoji-id=\"5258318620722733379\">🚫</tg-emoji> "
            f"<b>{name}</b> получает мут на <b>{minutes} минут</b> за спам."
        )

    @staticmethod
    async def _is_moderator(message: Message) -> bool:
        try:
            member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        except TelegramAPIError:
            return False

        return member.status in MODERATOR_STATUSES

    @staticmethod
    async def _reply(message: Message, text: str) -> None:
        try:
            await message.reply(text)
        except TelegramAPIError:
            pass