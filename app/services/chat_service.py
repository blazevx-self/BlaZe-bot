from app.database.repositories.chats_repository import chat_repository


class ChatService:
    """
    Сервис управления настройками Telegram-чата.

    Отвечает за работу с правилами, приветственными и прощальными сообщениями.
    """

    @staticmethod
    async def _get_chat(chat_id: int) -> dict:
        chat = await chat_repository.get_chat_by_id(chat_id=chat_id)

        if not chat:
            raise ValueError("The chat was not found")

        return chat


    @staticmethod
    async def upsert(chat_id: int, title: str) -> None:
        """Создает или обновляет чат"""

        chat = await chat_repository.upsert(chat_id=chat_id, title=title)

        return chat


    @staticmethod
    async def set_rules(chat_id: int, rules: str) -> None:
        """Создаёт или обновляет правила чата."""

        if not rules.strip():
            raise ValueError("The rules can't be empty")

        if len(rules) < 1 or len(rules) > 4000:
            raise ValueError("The number of characters cannot be less than 1 or more than 4000 characters")

        chat = await chat_service._get_chat(chat_id=chat_id)

        old_rules = chat['rules']

        if old_rules:
            rules = f"{old_rules}\n{rules}"

        return await chat_repository.update_rules(chat_id=chat_id, rules=rules)


    @staticmethod
    async def delete_rules(chat_id: int) -> None:
        """Удаляет правила чата"""

        chat = await chat_service._get_chat(chat_id=chat_id)

        if not chat['rules']:
            raise ValueError("There are no rules in this chat")

        return await chat_repository.update_rules(chat_id=chat_id, rules=None)


    @staticmethod
    async def get_rules(chat_id: int) -> str | None:
        """Возвращает правила чата"""

        chat = await chat_service._get_chat(chat_id=chat_id)

        return chat['rules']


    @staticmethod
    async def set_welcome_message(chat_id: int, welcome_message: str):
        """Создаёт или отправляет приветственное сообщение"""

        if not welcome_message.strip():
            raise ValueError("Welcome message can't be empty")

        if len(welcome_message) < 1 or len(welcome_message) > 4000:
            raise ValueError("The number of characters cannot be less than 1 or more than 4000 characters")

        await chat_service._get_chat(chat_id=chat_id)

        return await chat_repository.update_welcome_message(chat_id=chat_id, welcome_message=welcome_message)

    @staticmethod
    async def get_welcome_message(chat_id: int) -> str | None:
        """Возвращает приветственное сообщение"""

        chat = await chat_service._get_chat(chat_id=chat_id)

        return chat['welcome_message']

chat_service = ChatService()