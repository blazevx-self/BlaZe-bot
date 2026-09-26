from datetime import datetime, timedelta

from sqlalchemy import select, func

from app.database.repositories.base import Base
from app.database.models.chat.moderator_action import ModeratorActionOrm
from app.database.models.common.user import UserOrm

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
            target_user_id=target_user_id,
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
        within_minutes: int = 10
    ) -> int:
        stmt = select(func.count()).where(
            ModeratorActionOrm.chat_id == chat_id,
            ModeratorActionOrm.target_user_id == user_id,
            ModeratorActionOrm.action == ModerationActionType.WARN,
            ModeratorActionOrm.created_at >= func.now() - timedelta(minutes=within_minutes),
        )

        return await self.session.scalar(stmt) or 0

    async def get_user_history(
        self,
        chat_id: int,
        user_id: int,
        limit: int = 10
    ) -> list[tuple[ModeratorActionOrm, str | None]]:
        stmt = (
            select(ModeratorActionOrm, UserOrm.name)
            .outerjoin(UserOrm, UserOrm.id == ModeratorActionOrm.moderator_id)
            .where(
                ModeratorActionOrm.chat_id == chat_id,
                ModeratorActionOrm.target_user_id == user_id
            )
            .order_by(ModeratorActionOrm.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return [(action, name) for action, name in result.all()]

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