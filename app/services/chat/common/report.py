from html import escape

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import User
from aiogram.exceptions import TelegramAPIError

from cachetools import TTLCache

from app.core.constants.chat.report import REPORT_COOLDOWN
from app.core.exceptions.chat import ReportError

from app.database.repositories.chat.chat import ChatRepository

from app.utils.logger import chat_logger
from app.utils.truncate_text import truncate_text

_cooldowns: TTLCache = TTLCache(maxsize=10_000, ttl=REPORT_COOLDOWN.total_seconds())

class ReportService:
    def __init__(self, bot: Bot, chat_repo: ChatRepository):
        self.bot = bot
        self.chat_repo = chat_repo

    async def report(
        self,
        chat_id: int,
        reporter: User,
        target: User,
        reason: str | None,
        message_id: int | None,
    ) -> None:
        """Проверяет жалобу и возвращает модераторов, которых нужно упомянуть."""

        if target.id == reporter.id:
            raise ReportError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя пожаловаться на себя."
            )

        if target.id == self.bot.id:
            raise ReportError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя пожаловаться на бота."
            )

        if (chat_id, reporter.id) in _cooldowns:
            raise ReportError(
                "<tg-emoji emoji-id=\"5258258882022612173\">⏲️</tg-emoji> "
                "Жалобу можно отправлять раз в 5 минут."
            )

        chat = await self.chat_repo.get_chat_by_telegram_id(chat_id)

        if not chat or not chat.admin_chat_id:
            raise ReportError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Админ-чат не привязан."
            )

        try:
            member = await self.bot.get_chat_member(chat_id, target.id)
        except TelegramAPIError as e:
            raise ReportError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Пользователь не найден в чате."
            ) from e

        if member.status in {
            ChatMemberStatus.CREATOR,
            ChatMemberStatus.ADMINISTRATOR
        }:
            raise ReportError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя пожаловаться на администратора."
            )

        try:
            await self.bot.send_message(
                chat_id=chat.admin_chat_id,
                text=self._fmt_card(
                    chat_id=chat_id,
                    reporter=reporter,
                    target=target,
                    reason=reason,
                    message_id=message_id,
                ),
            )
        except TelegramAPIError as e:
            chat_logger.warning(
                f"[CHAT_REPORT] Send failed | chat_id={chat_id} "
                f"| admin_chat_id={chat.admin_chat_id} | {e}"
            )
            raise ReportError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Не удалось отправить жалобу в админ-чат."
            ) from e

        _cooldowns[(chat_id, reporter.id)] = True

        chat_logger.info(
            f"[CHAT_REPORT] Report sent | chat_id={chat_id} | "
            f"admin_chat_id={chat.admin_chat_id} | reporter_id={reporter.id} | "
            f"target_id={target.id}"
        )

    @staticmethod
    def _message_link(chat_id: int, message_id: int) -> str:
        return f"https://t.me/c/{str(chat_id).removeprefix('-100')}/{message_id}"

    @staticmethod
    def _mention(user_id: int, name: str) -> str:
        return f"<a href=\"tg://user?id={user_id}\">{escape(truncate_text(name))}</a>"

    def _fmt_card(
            self,
            chat_id: int,
            reporter: User,
            target: User,
            reason: str | None,
            message_id: int | None,
    ) -> str:
        return (
                "<tg-emoji emoji-id=\"5388947353791130731\">🚨</tg-emoji> "
                "<b>Жалоба</b>\n\n"
                "<tg-emoji emoji-id=\"6037622221625626773\">➡️</tg-emoji> "
                f"<b>Кого:</b> {self._mention(target.id, target.full_name)}\n"
                "<tg-emoji emoji-id=\"6032693626394382504\">👤</tg-emoji> "
                f"<b>Кто:</b> {self._mention(reporter.id, reporter.full_name)}\n"
                "<tg-emoji emoji-id=\"5778299625370817409\">📝</tg-emoji> "
                f"<b>Почему:</b> <i>{escape(reason) if reason else 'не сказали'}</i>"
                + (
                    f"\n\n<tg-emoji emoji-id=\"5258461531464539536\">📌</tg-emoji> "
                    f"<a href=\"{self._message_link(chat_id, message_id)}\">открыть сообщение</a>"
                    if message_id
                    else ""
                )
        )