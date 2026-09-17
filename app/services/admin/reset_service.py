from app.core.exceptions.user import UserNotFoundError

from app.types.entities.user import UserData
from app.types.services_result.admin import ResetResult

from app.database.repositories.user_repository import UserRepository
from app.database.repositories.ghoul_repository import GhoulRepository

from app.utils.logger import admin_logger

class ResetService:
    def __init__(self, user_repo: UserRepository, ghoul_repo: GhoulRepository):
        self.user_repo = user_repo
        self.ghoul_repo = ghoul_repo

    async def _resolve_user(self, query: str | int) -> UserData:
        user = await self.user_repo.resolve(query)

        if not user:
            raise UserNotFoundError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Пользователь не найден: {query}."
            )

        return user

    async def reset_ghoul(self, query: str | int, admin_id: int) -> ResetResult:
        user = await self._resolve_user(query)

        ghoul_deleted = await self.ghoul_repo.delete(user.telegram_id)

        admin_logger.info(
            f"[RESET_GHOUL] Ghoul reset | "
            f"admin_id={admin_id} | "
            f"user_id={user.telegram_id} | "
            f"deleted={ghoul_deleted}"
        )

        return ResetResult(
            telegram_id=user.telegram_id,
            user_deleted=False,
            ghoul_deleted=ghoul_deleted
        )

    async def reset_user(self, query: str | int, admin_id: int) -> ResetResult:
        user = await self._resolve_user(query)

        ghoul_deleted = await self.ghoul_repo.delete(user.telegram_id)
        user_deleted = await self.user_repo.delete(user.telegram_id)

        admin_logger.info(
            f"[RESET_USER] User reset | "
            f"admin_id={admin_id} | "
            f"user_id={user.telegram_id} | "
            f"user_deleted={user_deleted} | "
            f"ghoul_deleted={ghoul_deleted}"
        )

        return ResetResult(
            telegram_id=user.telegram_id,
            user_deleted=user_deleted,
            ghoul_deleted=ghoul_deleted
        )