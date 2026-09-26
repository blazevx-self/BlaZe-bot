from sqlalchemy import select, update, func
from sqlalchemy.dialects.postgresql import insert

from app.database.repositories.base import Base
from app.database.models.chat.chat_member import ChatMemberOrm
from app.database.models.chat.chat import ChatOrm
from app.database.models.common.user import UserOrm

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

    async def change_warnings(self, chat_id: int, user_id: int, delta: int) -> int:
        stmt = (
            update(ChatMemberOrm)
            .where(
                ChatMemberOrm.chat_id == chat_id,
                ChatMemberOrm.user_id == user_id,
            )
            .values(warnings=func.greatest(ChatMemberOrm.warnings + delta, 0))
            .returning(ChatMemberOrm.warnings)
        )

        return await self.session.scalar(stmt) or 0

    async def get_by_telegram_ids(
        self,
        chat_telegram_id: int,
        user_telegram_id: int
    ) -> ChatMemberOrm | None:
        stmt = (
            select(ChatMemberOrm)
            .join(ChatOrm, ChatOrm.id == ChatMemberOrm.chat_id)
            .join(UserOrm, UserOrm.id == ChatMemberOrm.user_id)
            .where(
                ChatOrm.telegram_id == chat_telegram_id,
                UserOrm.telegram_id == user_telegram_id
            )
        )

        return await self.session.scalar(stmt)

    async def increment_messages(self, chat_telegram_id: int, user_telegram_id: int) -> None:
        chat_id = select(ChatOrm.id).where(ChatOrm.telegram_id == chat_telegram_id).scalar_subquery()
        user_id = select(UserOrm.id).where(UserOrm.telegram_id == user_telegram_id).scalar_subquery()

        await self.session.execute(
            update(ChatMemberOrm)
            .where(
                ChatMemberOrm.chat_id == chat_id,
                ChatMemberOrm.user_id == user_id,
            )
            .values(messages_count=ChatMemberOrm.messages_count + 1)
        )