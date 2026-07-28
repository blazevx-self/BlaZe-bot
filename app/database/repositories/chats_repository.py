from app.database.base import DatabaseManager


class ChatRepository:
    @staticmethod
    async def upsert(chat_id: int, title: str) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("""
                INSERT OR IGNORE INTO chats (chat_id, title)
                VALUES (?, ?)
            """, (chat_id, title))

            await db.execute("""
                UPDATE chats
                SET title = ?
                WHERE chat_id = ?
            """, (title, chat_id))
            await db.commit()


    @staticmethod
    async def get_chat_by_id(chat_id: int) -> None:
        async with DatabaseManager.connect() as db:
            async with db.execute("""
                SELECT chat_id, creator_id, title, rules, welcome_message, goodbye_message, created_at
                FROM chats
                WHERE chat_id = ?
            """, (chat_id,)) as cursor:
                return await cursor.fetchone()


    @staticmethod
    async def update_rules(chat_id: int, rules: str | None) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("""
                UPDATE chats
                SET rules = ?
                WHERE chat_id = ?
            """, (rules, chat_id))
            await db.commit()


    @staticmethod
    async def update_welcome_message(chat_id: int, welcome_message: str | None) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("""
                UPDATE chats
                SET welcome_message = ?
                WHERE chat_id = ?
            """, (welcome_message, chat_id))
            await db.commit()


    @staticmethod
    async def update_goodbye_message(chat_id: int, goodbye_message: str | None) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("""
                UPDATE chats
                SET goodbye_message = ?
                WHERE chat_id = ?
            """, (goodbye_message, chat_id))
            await db.commit()


    @staticmethod
    async def get_all_chats():
        async with DatabaseManager.connect() as db:
            async with db.execute("""
                SELECT * 
                FROM chats
            """) as cursor:
                return await cursor.fetchall()

chat_repository = ChatRepository()