from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatMemberUnion

from app.core.constants.chat.chat_restrictions import MODERATOR_STATUSES
from app.core.exceptions.chat import ModerationError
from app.core.exceptions.user import UserNotFoundError

from app.types.entities.user import UserData

from app.database.repositories.common.user import UserRepository
from app.database.repositories import ChatRepository
from app.database.repositories.chat.moderator_action import ModeratorActionRepository

class ModerationService:
    def __init__(
        self,
        bot: Bot,
        user_repo: UserRepository,
        moderator_action_repo: ModeratorActionRepository,
        chat_repo: ChatRepository
    ):
        self.bot = bot
        self.user_repo = user_repo
        self.chat_repo = chat_repo
        self.moderator_action_repo = moderator_action_repo

    async def _get_chat(self, telegram_id: int) -> int:
        """Внутренний chats.id по Telegram ID чата - нужен для add_action."""

        chat = await self.chat_repo.get_chat_by_telegram_id(telegram_id=telegram_id)

        if not chat:
            raise ModerationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Чат не найден."
            )

        return chat.id

    async def _resolve_target(self, query: str | int) -> UserData:
        user = await self.user_repo.resolve(query)

        if not user:
            raise UserNotFoundError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Пользователь не найден: {query}."
            )

        return user

    async def _check_moderator(self, chat_id: int, moderator_id: int) -> None:
        """
        Создателю группы - можно всё.
        Админ - только если у него есть право ограничивать участников
        """

        member = await self.bot.get_chat_member(chat_id, moderator_id)

        if member.status == ChatMemberStatus.CREATOR:
            return

        if member.status == ChatMemberStatus.ADMINISTRATOR and member.can_restrict_members:
            return

        raise ModerationError(
            "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
            "У вас нет права ограничивать участников."
        )

    async def _check_target(
        self,
        chat_id: int,
        moderator_id: int,
        target: UserData
    ) -> ChatMemberUnion:
        if target.telegram_id == moderator_id:
            raise ModerationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя применить это к себе."
            )

        if target.telegram_id == self.bot.id:
            raise ModerationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя применить это к боту."
            )

        member = await self.bot.get_chat_member(chat_id, target.telegram_id)

        if member.status in MODERATOR_STATUSES:
            raise ModerationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя применить это к администратору чата."
            )

        return member

