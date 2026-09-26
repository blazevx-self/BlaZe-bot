from html import escape

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import User
from cachetools import TTLCache

from app.core.constants.chat.report import REPORT_COOLDOWN, MAX_MENTIONS
from app.core.exceptions.chat import ReportError

from app.utils.logger import chat_logger
from app.utils.truncate_text import truncate_text

_cooldowns: TTLCache = TTLCache(maxsize=10_000, ttl=REPORT_COOLDOWN.total_seconds())

class ReportService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def report(self, chat_id: int, reporter_id: int, target: User) -> list[User]:
        """Проверяет жалобу и возвращает модераторов, которых нужно упомянуть."""

        if target.id == reporter_id:
            raise ReportError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя пожаловаться на себя."
            )

        if target.id == self.bot.id:
            raise ReportError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя пожаловаться на бота."
            )

        if (chat_id, reporter_id) in _cooldowns:
            raise ReportError(
                "<tg-emoji emoji-id=\"5258258882022612173\">⏲️</tg-emoji> "
                "Жалобу можно отправлять раз в 5 минут."
            )

        admins = await self.bot.get_chat_administrators(chat_id)

        if any(admin.user.id == target.id for admin in admins):
            raise ReportError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя пожаловаться на администратора."
            )

        moderators = [
            admin.user
            for admin in admins
            if not admin.user.is_bot
            and not admin.is_anonymous
            and (admin.status == ChatMemberStatus.CREATOR or admin.can_restrict_members)
        ]

        if not moderators:
            raise ReportError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "В чате нет модераторов, которых можно позвать."
            )

        _cooldowns[(chat_id, reporter_id)] = True

        chat_logger.info(
            f"[CHAT_REPORT] Report sent | chat_id={chat_id} | "
            f"reporter_id={reporter_id} | target_id={target.id}"
        )

        return moderators[:MAX_MENTIONS]

    @staticmethod
    def _mention(user: User) -> str:
        if user.username:
            return f"@{user.username}"

        return f"<a href=\"tg://user?id={user.id}\">{escape(truncate_text(user.full_name))}</a>"

    def fmt_report(
        self,
        target: User,
        moderators: list[User],
        reason: str | None
    ) -> str:
        return (
            "<tg-emoji emoji-id=\"5388947353791130731\">🚨</tg-emoji> "
            f"<b>Жалоба на</b> {escape(truncate_text(target.full_name))}\n\n"
            "<tg-emoji emoji-id=\"5778299625370817409\">📝</tg-emoji> "
            f"<b>Причина:</b> <i>{escape(reason) if reason else 'Не указана'}</i>\n\n"
            "<tg-emoji emoji-id=\"6037622221625626773\">➡️</tg-emoji> "
            f"<b>Модераторы:</b> {', '.join(self._mention(m) for m in moderators)}"
        )