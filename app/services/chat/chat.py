from app.core.exceptions.chat import (
    ChatNotFoundError,
    ChatValidationError,
    ChatStateError
)

from app.database.models.chat.chat import ChatOrm
from app.database.repositories.chat.chat import ChatRepository

class ChatService:
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo

    async def _get_chat(self, telegram_id: int) -> ChatOrm:
        chat = await self.chat_repo.get_chat_by_telegram_id(telegram_id=telegram_id)

        if not chat:
            raise ChatNotFoundError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Чат не найден."
            )

        return chat

    async def upsert(self, telegram_id: int, title: str, username: str | None = None) -> ChatOrm:
        chat = await self.chat_repo.upsert(
            telegram_id=telegram_id,
            title=title,
            username=username
        )
        return chat

    async def set_rules(self, telegram_id: int, rules: str) -> ChatOrm:
        if not rules.strip():
            raise ChatValidationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Правила не могут быть пустыми."
            )

        if len(rules) < 1 or len(rules) > 4000:
            raise ChatValidationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Количество символов не может быть меньше 1 или больше 4000 символов."
            )

        chat = await self._get_chat(telegram_id=telegram_id)

        old_rules = chat.rules

        if old_rules:
            rules = f"{old_rules}\n{rules}"

        return await self.chat_repo.update_rules(
            telegram_id=telegram_id,
            rules=rules
        )

    async def delete_rules(self, telegram_id: int) -> ChatOrm:
        chat = await self._get_chat(telegram_id=telegram_id)

        if not chat.rules:
            raise ChatStateError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "В этом чате нет никаких правил."
            )

        return await self.chat_repo.update_rules(
            telegram_id=telegram_id,
            rules=None
        )

    async def set_welcome_message(self, telegram_id: int, welcome_message: str) -> ChatOrm:
        if not welcome_message.strip():
            raise ChatValidationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Приветственное сообщение не может быть пустым"
            )

        if len(welcome_message) < 1 or len(welcome_message) > 4000:
            raise ChatValidationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Количество символов не может быть меньше 1 или больше 4000 символов."
            )

        await self._get_chat(telegram_id=telegram_id)

        return await self.chat_repo.update_welcome_message(
            telegram_id=telegram_id,
            welcome_message=welcome_message
        )

    async def set_goodbye_message(self, telegram_id: int, goodbye_message: str) -> ChatOrm:
        if not goodbye_message.strip():
            raise ChatValidationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Прощальное сообщение не может быть пустым"
            )

        if len(goodbye_message) < 1 or len(goodbye_message) > 4000:
            raise ChatValidationError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Количество символов не может быть меньше 1 или больше 4000 символов."
            )

        await self._get_chat(telegram_id=telegram_id)

        return await self.chat_repo.update_goodbye_message(
            telegram_id=telegram_id,
            goodbye_message=goodbye_message
        )

    async def get_rules(self, telegram_id: int) -> str | None:
        chat = await self.chat_repo.get_chat_by_telegram_id(telegram_id)
        return chat.rules if chat else None

    async def get_welcome_message(self, telegram_id: int) -> str | None:
        chat = await self.chat_repo.get_chat_by_telegram_id(telegram_id)
        return chat.welcome_message if chat else None

    async def get_goodbye_message(self, telegram_id: int) -> str | None:
        chat = await self.chat_repo.get_chat_by_telegram_id(telegram_id)
        return chat.goodbye_message if chat else None