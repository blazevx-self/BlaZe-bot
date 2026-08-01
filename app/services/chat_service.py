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
            raise ValueError("Чат не найден.")

        return chat


    @staticmethod
    async def upsert(chat_id: int, title: str):
        """Создает или обновляет чат"""

        chat = await chat_repository.upsert(chat_id=chat_id, title=title)
        return chat


    @staticmethod
    async def set_rules(chat_id: int, rules: str):
        """Устанавливает правила чата."""

        if not rules.strip():
            raise ValueError("Правила не могут быть пустыми.")

        if len(rules) < 1 or len(rules) > 4000:
            raise ValueError("Количество символов не может быть меньше 1 или больше 4000 символов.")

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
        """Удаляет правила чата"""

        chat = await ChatService._get_chat(chat_id=chat_id)

        if not chat['rules']:
            raise ValueError("В этом чате нет никаких правил.")

        return await chat_repository.update_rules(
            chat_id=chat_id,
            rules=None
        )


    @staticmethod
    async def set_welcome_message(chat_id: int, welcome_message: str):
        """Устанавливает приветственное сообщение"""

        if not welcome_message.strip():
            raise ValueError("Приветственное сообщение не может быть пустым")

        if len(welcome_message) < 1 or len(welcome_message) > 4000:
            raise ValueError("Количество символов не может быть меньше 1 или больше 4000 символов.")

        await ChatService._get_chat(chat_id=chat_id)

        return await chat_repository.update_welcome_message(
            chat_id=chat_id,
            welcome_message=welcome_message
        )


    @staticmethod
    async def set_goodbye_message(chat_id: int, goodbye_message: str):
        """Устанавливает прощальное сообщение"""

        if not goodbye_message.strip():
            raise ValueError("Прощальное сообщение не может быть пустым")

        if len(goodbye_message) < 1 or len(goodbye_message) > 4000:
            raise ValueError("Количество символов не может быть меньше 1 или больше 4000 символов.")

        await ChatService._get_chat(chat_id=chat_id)

        return await chat_repository.update_goodbye_message(
            chat_id=chat_id,
            goodbye_message=goodbye_message
        )


    @staticmethod
    async def get_rules(chat_id: int) -> str | None:
        """Возвращает правила чата"""

        chat = await ChatService._get_chat(chat_id=chat_id)
        return chat['rules']


    @staticmethod
    async def get_welcome_message(chat_id: int) -> str | None:
        """Возвращает приветственное сообщение"""

        chat = await ChatService._get_chat(chat_id=chat_id)
        return chat['welcome_message']


    @staticmethod
    async def get_goodbye_message(chat_id: int) -> str | None:
        """Возвращает прощальное сообщение"""

        chat = await ChatService._get_chat(chat_id=chat_id)
        return chat['goodbye_message']

chat_service = ChatService()