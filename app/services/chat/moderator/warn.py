from html import escape

from aiogram import Bot

from app.core.constants.chat.count_warn import MAX_WARNINGS
from app.core.enums.moderator_action import ModerationActionType
from app.core.exceptions.chat import ModerationError

from app.database.repositories.common.user import UserRepository
from app.database.repositories import ChatRepository
from app.database.repositories.chat.chat_member import ChatMemberRepository
from app.database.repositories.chat.moderator_action import ModeratorActionRepository

from app.types.services_result.chat import ModeratorActionResult
from app.services.chat.moderator.moderation import ModerationService

from app.utils.logger import chat_logger
from app.utils.truncate_text import truncate_text

class ChatWarnService(ModerationService):
    def __init__(
        self,
        bot: Bot,
        user_repo: UserRepository,
        moderator_action_repo: ModeratorActionRepository,
        chat_repo: ChatRepository,
        chat_member_repo: ChatMemberRepository
    ):
        super().__init__(bot, user_repo, moderator_action_repo, chat_repo)
        self.chat_member_repo = chat_member_repo

    async def warn(
        self,
        chat_id: int,
        moderator_id: int,
        query: str | int,
        reason: str | None = None
    ) -> ModeratorActionResult:
        await self._check_moderator(chat_id, moderator_id)

        target = await self._resolve_target(query)
        await self._check_target(chat_id, moderator_id, target)

        chat_pk = await self._get_chat(chat_id)

        # записи может не быть, если человек еще не писал в этот чат
        await self.chat_member_repo.upsert(chat_id=chat_pk, user_id=target.id)
        warnings = await self.chat_member_repo.change_warnings(chat_pk, target.id, 1)

        if warnings >= MAX_WARNINGS:
            await self.chat_member_repo.change_warnings(chat_pk, target.id, -warnings)

        moderator = await self.user_repo.get(moderator_id)

        await self.moderator_action_repo.add_action(
            chat_id=chat_pk,
            target_user_id=target.id,
            moderator_id=moderator.id if moderator else None,
            action=ModerationActionType.WARN,
            reason=reason
        )

        chat_logger.info(
            f"[CHAT_WARN] User warned | chat_id={chat_id} | user_id={target.telegram_id} | "
            f"moderator_id={moderator_id} | warnings={warnings}/{MAX_WARNINGS} | reason={reason!r}"
        )

        return ModeratorActionResult(
            action=ModerationActionType.WARN,
            user=target,
            reason=reason,
            warnings=warnings
        )

    async def unwarn(
        self,
        chat_id: int,
        moderator_id: int,
        query: str | int
    ) -> ModeratorActionResult:
        await self._check_moderator(chat_id, moderator_id)

        target = await self._resolve_target(query)
        chat_pk = await self._get_chat(chat_id)

        member = await self.chat_member_repo.get(chat_id=chat_pk, user_id=target.id)

        if not member or member.warnings == 0:
            raise ModerationError(
                "<tg-emoji emoji-id=\"5386470514871003633\">☕️</tg-emoji> "
                "У пользователя нет предупреждений."
            )

        warnings = await self.chat_member_repo.change_warnings(chat_pk, target.id, -1)
        moderator = await self.user_repo.get(moderator_id)

        await self.moderator_action_repo.add_action(
            chat_id=chat_pk,
            target_user_id=target.id,
            moderator_id=moderator.id if moderator else None,
            action=ModerationActionType.UNWARN
        )

        chat_logger.info(
            f"[CHAT_UNWARN] Warning removed | chat_id={chat_id} | user_id={target.telegram_id} | "
            f"moderator_id={moderator_id} | warnings={warnings}/{MAX_WARNINGS}"
        )

        return ModeratorActionResult(
            action=ModerationActionType.UNWARN,
            user=target,
            warnings=warnings
        )

    @staticmethod
    def fmt_warn_result(result: ModeratorActionResult) -> str:
        text = (
            "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
            f"Пользователь <code>{result.user.telegram_id}</code> "
            f"({escape(truncate_text(result.user.name))}) "
            f"<b>получил предупреждение {result.warnings}/{MAX_WARNINGS}.</b>\n\n"
            "<tg-emoji emoji-id=\"5778299625370817409\">📝</tg-emoji> "
            f"<b>Причина:</b> <i>{escape(result.reason) if result.reason else 'Не указана'}</i>"
        )

        if result.warnings >= MAX_WARNINGS:
            text += (
                "\n\n<tg-emoji emoji-id=\"5258318620722733379\">🚫</tg-emoji> "
                "<b>Лимит предупреждений достигнут, счётчик сброшен.</b>\n\n"
                "<tg-emoji emoji-id=\"5258461531464539536\">📌</tg-emoji> "
                "<b>Выберите наказание:</b> /ban_chat, /mute_chat или /kick_chat"
            )

        return text

    @staticmethod
    def fmt_unwarn_result(result: ModeratorActionResult) -> str:
        return (
            "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
            f"С пользователя <code>{result.user.telegram_id}</code> "
            f"({escape(truncate_text(result.user.name))}) <b>снято предупреждение.</b>\n\n"
            f"<b>Осталось:</b> <code>{result.warnings}/{MAX_WARNINGS}</code>."
        )