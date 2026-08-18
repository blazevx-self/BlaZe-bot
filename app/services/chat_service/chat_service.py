from app.database.repositories.chats_repository import chat_repository
from app.core.exceptions.chat import ChatNotFoundError, ChatValidationError, ChatStateError

class ChatService:
    @staticmethod
    async def _get_chat(chat_id: int) -> dict:
        chat = await chat_repository.get_chat_by_id(chat_id=chat_id)

        if not chat:
            raise ChatNotFoundError("Чат не найден.")

        return chat


    @staticmethod
    async def upsert(chat_id: int, title: str):
        chat = await chat_repository.upsert(chat_id=chat_id, title=title)
        return chat

    @staticmethod
    async def set_rules(chat_id: int, rules: str):
        if not rules.strip():
            raise ChatValidationError("Правила не могут быть пустыми.")

        if len(rules) > 4000:
            raise ChatValidationError("Количество символов не может быть меньше 1 или больше 4000 символов.")

        chat = await ChatService._get_chat(chat_id=chat_id)

        old_rules = chat['rules']

        if old_rules:
            rules = f"{old_rules}\n{rules}"

        return await chat_repository.update_rules(
            chat_id=chat_id,
            rules=rules
        )

    @staticmethod
    async def delete_rules(chat_id: int):
        chat = await ChatService._get_chat(chat_id=chat_id)

        if not chat['rules']:
            raise ChatStateError("В этом чате нет никаких правил.")

        return await chat_repository.update_rules(
            chat_id=chat_id,
            rules=None
        )

    @staticmethod
    async def set_welcome_message(chat_id: int, welcome_message: str):
        if not welcome_message.strip():
            raise ChatValidationError("Приветственное сообщение не может быть пустым")

        if len(welcome_message) > 4000:
            raise ChatValidationError("Количество символов не может быть меньше 1 или больше 4000 символов.")

        await ChatService._get_chat(chat_id=chat_id)

        return await chat_repository.update_welcome_message(
            chat_id=chat_id,
            welcome_message=welcome_message
        )

    @staticmethod
    async def set_goodbye_message(chat_id: int, goodbye_message: str):
        if not goodbye_message.strip():
            raise ChatValidationError("Прощальное сообщение не может быть пустым")

        if len(goodbye_message) > 4000:
            raise ChatValidationError("Количество символов не может быть меньше 1 или больше 4000 символов.")

        await ChatService._get_chat(chat_id=chat_id)

        return await chat_repository.update_goodbye_message(
            chat_id=chat_id,
            goodbye_message=goodbye_message
        )


    @staticmethod
    async def get_rules(chat_id: int) -> str | None:
        chat = await ChatService._get_chat(chat_id=chat_id)
        return chat['rules']

    @staticmethod
    async def get_welcome_message(chat_id: int) -> str | None:
        chat = await ChatService._get_chat(chat_id=chat_id)
        return chat['welcome_message']

    @staticmethod
    async def get_goodbye_message(chat_id: int) -> str | None:
        chat = await ChatService._get_chat(chat_id=chat_id)
        return chat['goodbye_message']

chat_service = ChatService()