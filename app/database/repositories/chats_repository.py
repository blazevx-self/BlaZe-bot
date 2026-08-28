from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.database.repositories.base import Base
from app.database.models.chat import ChatOrm

from app.core.exceptions.chat import ChatNotFoundError

class ChatRepository(Base):
    async def upsert(
        self, 
        telegram_id: int, 
        title: str, 
        username: str | None = None
    ) -> ChatOrm:
        stmt = (
            insert(ChatOrm)
            .values(
                telegram_id=telegram_id,
                title=title,
                username=username
            )
            .on_conflict_do_update(
                index_elements=[ChatOrm.telegram_id],
                set_={
                    "title": title,
                    "username": username
                }
            )
            .returning(ChatOrm)
        )
        
        chat = await self.session.scalar(stmt)

        if chat is None:
            ChatNotFoundError(f"Chat ({telegram_id}) not found after upsert")

        return chat

    async def get_chat_by_telegram_id(self, telegram_id: int) -> ChatOrm | None:
        stmt = select(ChatOrm).where(ChatOrm.telegram_id == telegram_id)
        return await self.session.scalar(stmt)

    async def update_rules(self, telegram_id: int, rules: str | None) -> ChatOrm:
        stmt = (
            update(ChatOrm)
            .where(ChatOrm.telegram_id == telegram_id)
            .values(rules=rules)
            .returning(ChatOrm)
        )
        
        chat = await self.session.scalar(stmt)

        if chat is None:
            raise ChatNotFoundError(f"Chat ({telegram_id}) not found")

        return chat

    async def update_welcome_message(self, telegram_id: int, welcome_message: str | None) -> ChatOrm:
        stmt = (
            update(ChatOrm)
            .where(ChatOrm.telegram_id == telegram_id)
            .values(welcome_message=welcome_message)
            .returning(ChatOrm)
        )
        
        chat = await self.session.scalar(stmt)
        
        if chat is None:
            raise ChatNotFoundError(f"Chat ({telegram_id}) not found")

        return chat

    async def update_goodbye_message(self, telegram_id: int, goodbye_message: str | None) -> ChatOrm:
        stmt = (
            update(ChatOrm)
            .where(ChatOrm.telegram_id == telegram_id)
            .values(goodbye_message=goodbye_message)
            .returning(ChatOrm)
        )
        
        chat = await self.session.scalar(stmt)
        
        if chat is None:
            raise ChatNotFoundError(f"Chat ({telegram_id}) not found")
        
        return chat

    async def get_all(self) -> list[ChatOrm]:
        result = await self.session.scalars(select(ChatOrm))
        return list(result)