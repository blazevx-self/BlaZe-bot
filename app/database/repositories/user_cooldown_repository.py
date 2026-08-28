import time

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

from app.core.enums.cooldown_action import CooldownAction
from app.database.models.user_cooldown import UserCooldownOrm

from app.database.repositories.base import Base

class UserCooldownRepository(Base):
    async def get(self, telegram_id: int, action: CooldownAction) -> UserCooldownOrm | None:
        stmt = select(UserCooldownOrm).where(
            UserCooldownOrm.telegram_id == telegram_id,
            UserCooldownOrm.action == action
        )
        
        return await self.session.scalar(stmt)

    async def get_remaining(self, telegram_id: int, action: CooldownAction) -> int:
        cooldown = await self.get(
            telegram_id=telegram_id,
            action=action
        )
        
        if not cooldown:
            return 0
        
        remaining = cooldown.expires_at - int(time.time())
        
        if remaining <= 0:
            await self.delete(
                telegram_id=telegram_id,
                action=action
            )
            return 0
        
        return remaining

    async def set(self, telegram_id: int, action: CooldownAction, duration: int) -> UserCooldownOrm:
        expires_at = int(time.time()) + duration
        
        stmt = (
            insert(UserCooldownOrm)
            .values(
                telegram_id=telegram_id,
                action=action,
                expires_at=expires_at
            )
            .on_conflict_do_update(
                constraint="uq_user_cooldown_action",
                set_={"expires_at": expires_at}
            )
            .returning(UserCooldownOrm)
        )
        
        return await self.session.scalar(stmt)

    async def delete(self, telegram_id: int, action: CooldownAction) -> None:
        stmt = delete(UserCooldownOrm).where(
            UserCooldownOrm.telegram_id == telegram_id,
            UserCooldownOrm.action == action
        )
        await self.session.execute(stmt)

    async def cleanup_expired(self) -> None:
        stmt = delete(UserCooldownOrm).where(
            UserCooldownOrm.expires_at <= int(time.time())
        )
        await self.session.execute(stmt)