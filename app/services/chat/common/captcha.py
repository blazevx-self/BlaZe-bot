import asyncio

from dataclasses import dataclass
from datetime import timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ChatPermissions, InlineKeyboardMarkup, User

from app.core.constants.chat.captcha import CAPTCHA_TIMEOUT
from app.core.constants.chat.mute_permissions import MUTED
from app.core.exceptions.chat import CaptchaError

from app.utils.logger import chat_logger

@dataclass
class _Pending:
    message_id: int
    task: asyncio.Task

class CaptchaService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self._pending: dict[tuple[int, int], _Pending] = {}

    def is_pending(self, chat_id: int, user_id: int) -> bool:
        return (chat_id, user_id) in self._pending

    async def start(
        self,
        chat_id: int,
        user: User,
        reply_markup: InlineKeyboardMarkup,
        text: str
    ) -> None:
        key = (chat_id, user.id)
        self._cancel(key)

        try:
            await self.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user.id,
                permissions=MUTED
            )

            message = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup
            )
        except TelegramAPIError as e:
            chat_logger.warning(f"[CAPTCHA] Start failed | chat_id={chat_id} | user_id={user.id} | {e}")

            raise CaptchaError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Не удалось запустить капчу: у бота нет прав."
            ) from e

        task = asyncio.create_task(self._timeout(chat_id, user.id))
        self._pending[key] = _Pending(message_id=message.message_id, task=task)

    async def verify(self, chat_id: int, user_id: int) -> None:
        pending = self._pop(chat_id, user_id)

        if not pending:
            raise CaptchaError("Капча не найдена.")

        try:
            chat = await self.bot.get_chat(chat_id)

            await self.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=chat.permissions or ChatPermissions(can_send_messages=True)
            )
        except TelegramAPIError as e:
            chat_logger.warning(f"[CAPTCHA] Verify failed | chat_id={chat_id} | user_id={user_id} | {e}")

            raise CaptchaError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Не удалось снять ограничение."
            ) from e

        await self._delete(chat_id, pending.message_id)

    async def fail(self, chat_id: int, user_id: int) -> None:
        pending = self._pop(chat_id, user_id)

        try:
            await self.bot.ban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                until_date=timedelta(seconds=40)
            )
        except TelegramAPIError as e:
            chat_logger.warning(f"[CAPTCHA] Kick failed | chat_id={chat_id} | user_id={user_id} | {e}")

        if pending:
            await self._delete(chat_id, pending.message_id)

    def cancel(self, chat_id: int, user_id: int) -> None:
        """Выход из чата до кнопки — не кикать."""
        self._pop(chat_id, user_id)

    async def _timeout(self, chat_id: int, user_id: int) -> None:
        await asyncio.sleep(CAPTCHA_TIMEOUT)
        await self.fail(chat_id, user_id)

    def _pop(self, chat_id: int, user_id: int) -> _Pending | None:
        pending = self._pending.get((chat_id, user_id), None)

        if pending and not pending.task.done():
            pending.task.cancel()

        return pending

    def _cancel(self, key: tuple[int, int]) -> None:
        pending = self._pending.pop(key, None)

        if pending and not pending.task.done():
            pending.task.cancel()

    async def _delete(self, chat_id: int, message_id: int) -> None:
        try:
            await self.bot.delete_message(chat_id, message_id)
        except TelegramAPIError:
            pass
