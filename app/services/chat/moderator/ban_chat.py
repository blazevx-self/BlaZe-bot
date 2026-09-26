from html import escape
from datetime import datetime

from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError

from app.core.enums.moderator_action import ModerationActionType
from app.core.exceptions.chat import ModerationError

from app.types.services_result.chat import ModeratorActionResult
from app.services.chat.moderator.moderation import ModerationService

from app.utils.logger import chat_logger
from app.utils.truncate_text import truncate_text
from app.utils.time import parse_duration

class ChatBanService(ModerationService):
    async def ban(
        self,
        chat_id: int,
        moderator_id: int,
        query: str | int,
        duration: str | None = None,
        reason: str | None = None,
    ) -> ModeratorActionResult:
        await self._check_moderator(chat_id, moderator_id)

        target = await self._resolve_target(query)
        member = await self._check_target(chat_id, moderator_id, target)

        if member.status == ChatMemberStatus.KICKED:
            raise ModerationError(
                "<tg-emoji emoji-id=\"5258318620722733379\">🚫</tg-emoji> "
                "Пользователь уже забанен."
            )

        delta = parse_duration(duration)

        if duration and delta is None:
            reason = f"{duration} {reason or ''}".strip()

        try:
            await self.bot.ban_chat_member(
                chat_id=chat_id,
                user_id=target.telegram_id,
                until_date=delta
            )
        except TelegramAPIError as e:
            chat_logger.warning(
                f"[CHAT BAN] Failed | chat_id={chat_id} "
                f"| user_id={target.telegram_id} | {e}"
            )

            raise ModerationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Не удалось забанить: у бота нет прав."
            ) from e

        until = datetime.now() + delta if delta else None
        moderator = await self.user_repo.get(moderator_id)

        await self.moderator_action_repo.add_action(
            chat_id=await self._get_chat(chat_id),
            target_user_id=target.id,
            moderator_id=moderator.id if moderator else None,
            action=ModerationActionType.BAN,
            reason=reason,
            expires_at=until
        )

        chat_logger.info(
            f"[CHAT_BAN] User banned | chat_id={chat_id} | user_id={target.telegram_id} | "
            f"moderator_id={moderator_id} | until={until} | reason={reason!r}"
        )

        return ModeratorActionResult(
            action=ModerationActionType.BAN,
            user=target,
            reason=reason,
            until=until
        )

    async def unban(self, chat_id: int, moderator_id: int, query: str | int) -> ModeratorActionResult:
        await self._check_moderator(chat_id, moderator_id)

        target = await self._resolve_target(query)
        member = await self.bot.get_chat_member(chat_id, target.telegram_id)

        if member.status != ChatMemberStatus.KICKED:
            raise ModerationError(
                "<tg-emoji emoji-id=\"5386470514871003633\">☕️</tg-emoji> "
                "Пользователь не забанен."
            )

        try:
            await self.bot.unban_chat_member(
                chat_id=chat_id,
                user_id=target.telegram_id,
                only_if_banned=True
            )
        except TelegramAPIError as e:
            chat_logger.warning(
                f"[CHAT UNBAN] Failed | chat_id={chat_id} "
                f"| user_id={target.telegram_id} | {e}"
            )

            raise ModerationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Не удалось разбанить: у бота нет прав."
            ) from e

        moderator = await self.user_repo.get(moderator_id)

        await self.moderator_action_repo.add_action(
            chat_id=await self._get_chat(chat_id),
            target_user_id=target.id,
            moderator_id=moderator.id if moderator else None,
            action=ModerationActionType.UNBAN,
        )

        chat_logger.info(
            f"[CHAT_UNBAN] User unbanned | chat_id={chat_id} | user_id={target.telegram_id} | "
            f"moderator_id={moderator_id}"
        )

        return ModeratorActionResult(
            action=ModerationActionType.UNBAN,
            user=target
        )

    @staticmethod
    def fmt_ban_result(result: ModeratorActionResult) -> str:
        until = (
            f"до {result.until.strftime('%d.%m.%Y %H:%M')}"
            if result.until
            else "навсегда"
        )

        return (
            "<tg-emoji emoji-id=\"5258318620722733379\">🚫</tg-emoji> "
            f"Пользователь <code>{result.user.telegram_id}</code> "
            f"({escape(truncate_text(result.user.name))}) <b>заблокирован {until}.</b>\n\n"
            "<tg-emoji emoji-id=\"5778299625370817409\">📝</tg-emoji> "
            f"<b>Причина:</b> <i>{escape(result.reason) if result.reason else 'Не указана'}</i>"
        )

    @staticmethod
    def fmt_unban_result(result: ModeratorActionResult) -> str:
        return (
            "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
            f"Пользователь <code>{result.user.telegram_id}</code> "
            f"({escape(truncate_text(result.user.name))}) <b>разблокирован.</b>"
        )