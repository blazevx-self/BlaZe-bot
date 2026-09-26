from html import escape
from datetime import datetime

from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ChatPermissions

from app.core.constants.chat.mute_permissions import MUTED
from app.core.enums.moderator_action import ModerationActionType
from app.core.exceptions.chat import ModerationError

from app.types.services_result.chat import ModeratorActionResult
from app.services.chat.moderator.moderation import ModerationService

from app.utils.logger import chat_logger
from app.utils.truncate_text import truncate_text
from app.utils.time import parse_duration

class ChatMuteService(ModerationService):
    async def mute(
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
                "Пользователь забанен."
            )

        if member.status == ChatMemberStatus.RESTRICTED and not member.can_send_messages:
            raise ModerationError(
                "<tg-emoji emoji-id=\"5258267368877989660\">🔇</tg-emoji> "
                "Пользователь уже в муте."
            )

        delta = parse_duration(duration)

        if duration and delta is None:
            reason = f"{duration} {reason or ''}".strip()

        try:
            await self.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=target.telegram_id,
                permissions=MUTED,
                until_date=delta
            )
        except TelegramAPIError as e:
            chat_logger.warning(
                f"[CHAT_MUTE] Failed | chat_id={chat_id} "
                f"| user_id={target.telegram_id} | {e}"
            )

            raise ModerationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Не удалось замутить: у бота нет прав."
            ) from e

        until = datetime.now() + delta if delta else None
        moderator = await self.user_repo.get(moderator_id)

        await self.moderator_action_repo.add_action(
            chat_id=await self._get_chat(chat_id),
            target_user_id=target.id,
            moderator_id=moderator.id if moderator else None,
            action=ModerationActionType.MUTE,
            reason=reason,
            expires_at=until
        )

        chat_logger.info(
            f"[CHAT_MUTE] User muted | chat_id={chat_id} | user_id={target.telegram_id} | "
            f"moderator_id={moderator_id} | until={until} | reason={reason!r}"
        )

        return ModeratorActionResult(
            action=ModerationActionType.MUTE,
            user=target,
            reason=reason,
            until=until
        )

    async def unmute(
        self,
        chat_id: int,
        moderator_id: int,
        query: str | int
    ) -> ModeratorActionResult:
        await self._check_moderator(chat_id, moderator_id)

        target = await self._resolve_target(query)
        member = await self.bot.get_chat_member(chat_id, target.telegram_id)

        if member.status != ChatMemberStatus.RESTRICTED or member.can_send_messages:
            raise ModerationError(
                "<tg-emoji emoji-id=\"5386470514871003633\">☕️</tg-emoji> "
                "Пользователь не в муте."
            )

        try:
            chat = await self.bot.get_chat(chat_id)

            await self.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=target.telegram_id,
                permissions=chat.permissions or ChatPermissions(can_send_messages=True),
            )
        except TelegramAPIError as e:
            chat_logger.warning(
                f"[CHAT_UNMUTE] Failed | chat_id={chat_id} "
                f"| user_id={target.telegram_id} | {e}"
            )

            raise ModerationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Не удалось размутить: у бота нет прав."
            ) from e

        moderator = await self.user_repo.get(moderator_id)

        await self.moderator_action_repo.add_action(
            chat_id=await self._get_chat(chat_id),
            target_user_id=target.id,
            moderator_id=moderator.id if moderator else None,
            action=ModerationActionType.UNMUTE
        )

        chat_logger.info(
            f"[CHAT_UNMUTE] User unmuted | chat_id={chat_id} | user_id={target.telegram_id} | "
            f"moderator_id={moderator_id}"
        )

        return ModeratorActionResult(
            action=ModerationActionType.UNMUTE,
            user=target,
        )

    @staticmethod
    def fmt_mute_result(result: ModeratorActionResult) -> str:
        until = (
            f"до {result.until.strftime('%d.%m.%Y %H:%M')}"
            if result.until
            else "навсегда"
        )

        return (
            "<tg-emoji emoji-id=\"5258267368877989660\">🔇</tg-emoji> "
            f"Пользователь <code>{result.user.telegram_id}</code> "
            f"({escape(truncate_text(result.user.name))}) <b>замучен {until}.</b>\n\n"
            "<tg-emoji emoji-id=\"5778299625370817409\">📝</tg-emoji> "
            f"<b>Причина:</b> <i>{escape(result.reason) if result.reason else 'Не указана'}</i>"
        )

    @staticmethod
    def fmt_unmute_result(result: ModeratorActionResult) -> str:
        return (
            "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
            f"Пользователь <code>{result.user.telegram_id}</code> "
            f"({escape(truncate_text(result.user.name))}) <b>размучен.</b>"
        )