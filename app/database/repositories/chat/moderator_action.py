from datetime import datetime, timedelta
from sqlalchemy import select

from app.database.repositories.base import Base
from app.database.models.chat.moderator_action import ModeratorActionOrm

from app.core.enums.moderator_action import ModerationActionType

class ModeratorActionRepository(Base):
    async def add_action(
        self,
        chat_id: int,
        target_user_id: int,
        action: ModerationActionType,
        reason: str | None = None,
        moderator_id: int | None = None,
        expires_at: datetime | None = None,
    ) -> ModeratorActionOrm:
        new_action = ModeratorActionOrm(
            chat_id=chat_id,
            target_user_at=target_user_id,
            action=action,
            reason=reason,
            moderator_id=moderator_id,
            expires_at=expires_at
        )

        self.session.add(new_action)
        await self.session.flush()

        return new_action

    async def count_active_warnings(
        self,
        chat_id: int,
        user_id: int,
        within_hours: int = 24
    ) -> int:
        cutoff_time = datetime.now() - timedelta(hours=within_hours)

        stmt = select(ModeratorActionOrm).where(
            ModeratorActionOrm.chat_id == chat_id,
            ModeratorActionOrm.target_user_id == user_id,
            ModeratorActionOrm.action == ModerationActionType.WARN,
            ModeratorActionOrm.created_at >= cutoff_time,
        )

        result = await self.session.scalars(stmt)

        return len(result.all())

    async def get_user_history(
        self,
        chat_id: int,
        user_id: int,
        limit: int = 20
    ) -> list[ModeratorActionOrm]:
        stmt = (
            select(ModeratorActionOrm)
            .where(
                ModeratorActionOrm.chat_id == chat_id,
                ModeratorActionOrm.target_user_id == user_id
            )
            .order_by(ModeratorActionOrm.created_at.desc())
            .limit(limit)
        )

        result = await self.session.scalars(stmt)

        return list(result)

    async def get_active_restriction(
        self,
        chat_id: int,
        user_id: int,
        action_type: ModerationActionType
    ) -> ModeratorActionOrm | None:
        stmt = (
            select(ModeratorActionOrm)
            .where(
                ModeratorActionOrm.chat_id == chat_id,
                ModeratorActionOrm.target_user_id == user_id,
                ModeratorActionOrm.action == action_type,
                ModeratorActionOrm.expires_at > datetime.now()
            )
            .order_by(ModeratorActionOrm.created_at.desc())
            .limit(1)
        )
        return await self.session.scalar(stmt)