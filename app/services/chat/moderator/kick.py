from html import escape

from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError

from app.core.enums.moderator_action import ModerationActionType
from app.core.exceptions.chat import ModerationError

from app.types.services_result.chat import ModeratorActionResult
from app.services.chat.moderator.moderation import ModerationService

from app.utils.logger import chat_logger
from app.utils.truncate_text import truncate_text

class ChatKickService(ModerationService):
    async def kick(
        self,
        chat_id: int,
        moderator_id: int,
        query: str | int,
        reason: str | None = None,
    ) -> ModeratorActionResult:
        await self._check_moderator(chat_id, moderator_id)

        target = await self._resolve_target(query)
        member = await self._check_target(chat_id, moderator_id, target)

        # RESTRICTED бывает и у тех, кто уже вышел: тогда is_member=False
        not_in_chat = (
            member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)
            or (member.status == ChatMemberStatus.RESTRICTED and not member.is_member)
        )

        if not_in_chat:
            raise ModerationError(
                "<tg-emoji emoji-id=\"5386470514871003633\">☕️</tg-emoji> "
                "Пользователя нет в чате."
            )

        try:
            await self.bot.ban_chat_member(
                chat_id=chat_id,
                user_id=target.telegram_id
            )
        except TelegramAPIError as e:
            chat_logger.warning(
                f"[CHAT_KICK] Failed | chat_id={chat_id} "
                f"| user_id={target.telegram_id} | {e}"
            )

            raise ModerationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Не удалось кикнуть: у бота нет прав."
            ) from e

        try:
            await self.bot.unban_chat_member(
                chat_id=chat_id,
                user_id=target.telegram_id,
                only_if_banned=True
            )
        except TelegramAPIError as e:
            # Кик прошёл, но человек остался в бане. Говорим об этом прямо
            chat_logger.error(
                f"[CHAT_KICK] Unban after kick failed | chat_id={chat_id} "
                f"| user_id={target.telegram_id} | {e}"
            )

            raise ModerationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Пользователь исключён, но остался в бане. Используйте /unban_chat."
            ) from e

        moderator = await self.user_repo.get(moderator_id)

        await self.moderator_action_repo.add_action(
            chat_id=await self._get_chat(chat_id),
            target_user_id=target.id,
            moderator_id=moderator.id if moderator else None,
            action=ModerationActionType.KICK,
            reason=reason
        )

        chat_logger.info(
            f"[CHAT_KICK] User kicked | chat_id={chat_id} | user_id={target.telegram_id} | "
            f"moderator_id={moderator_id} | reason={reason!r}"
        )

        return ModeratorActionResult(
            action=ModerationActionType.KICK,
            user=target,
            reason=reason
        )

    @staticmethod
    def fmt_kick_result(result: ModeratorActionResult) -> str:
        return (
            "<tg-emoji emoji-id=\"5258318620722733379\">🚫</tg-emoji> "
            f"Пользователь <code>{result.user.telegram_id}</code> "
            f"({escape(truncate_text(result.user.name))}) <b>исключён из чата.</b>\n\n"
            "<tg-emoji emoji-id=\"5778299625370817409\">📝</tg-emoji> "
            f"<b>Причина:</b> <i>{escape(result.reason) if result.reason else 'Не указана'}</i>"
        )
