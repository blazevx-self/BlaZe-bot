from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.database.repositories.base import Base
from app.database.models.chat.chat_member import ChatMemberOrm

from app.core.exceptions.chat import ChatMemberNotFoundError

class ChatMemberRepository(Base):
    async def upsert(self, chat_id: int, user_id: int) -> ChatMemberOrm:
        stmt = (
            insert(ChatMemberOrm)
            .values(
                chat_id=chat_id,
                user_id=user_id,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    ChatMemberOrm.chat_id,
                    ChatMemberOrm.user_id,
                ]
            )
            .returning(ChatMemberOrm)
        )

        member = await self.session.scalar(stmt)

        if member is not None:
            return member

        stmt = select(ChatMemberOrm).where(
            ChatMemberOrm.chat_id == chat_id,
            ChatMemberOrm.user_id == user_id
        )

        member = await self.session.scalar(stmt)

        if member is None:
            raise RuntimeError(f"Chat member ({chat_id}, {user_id}) not found after upsert")

        return member

    async def get(self, chat_id: int, user_id: int) -> ChatMemberOrm:
        stmt = select(ChatMemberOrm).where(
            ChatMemberOrm.chat_id == chat_id,
            ChatMemberOrm.user_id == user_id,
        )
        return await self.session.scalar(stmt)

    async def update_warnings(self, chat_id: int, user_id: int, warnings: int) -> ChatMemberOrm:
        stmt = (
            update(ChatMemberOrm)
            .where(
                ChatMemberOrm.chat_id == chat_id,
                ChatMemberOrm.user_id == user_id
            )
            .values(warnings=warnings)
            .returning(ChatMemberOrm)
        )

        member = await self.session.scalar(stmt)

        if member is None:
            raise ChatMemberNotFoundError(f"Chat member ({chat_id}, {user_id}) not found")

        return member