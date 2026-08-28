from app.core.enums.cooldown_action import CooldownAction

from app.database.models.user_cooldown import UserCooldownOrm
from app.database.repositories.user_cooldown_repository import UserCooldownRepository

class CooldownService:
    def __init__(self, user_cooldown_repo: UserCooldownRepository):
        self.user_cooldown_repo = user_cooldown_repo

    async def remaining(self, telegram_id: int, action: CooldownAction) -> int:
        return await self.user_cooldown_repo.get_remaining(
            telegram_id=telegram_id,
            action=action
        )

    async def set(self, telegram_id: int, action: CooldownAction, duration: int) -> UserCooldownOrm:
        return await self.user_cooldown_repo.set(
            telegram_id=telegram_id,
            action=action,
            duration=duration
        )

    async def reset(self, telegram_id: int, action: CooldownAction) -> None:
        await self.user_cooldown_repo.delete(
            telegram_id=telegram_id,
            action=action
        )
