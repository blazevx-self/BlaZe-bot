from html import escape

from app.core.enums.death_cause import DeathCause
from app.core.exceptions.user import UserNotFoundError

from app.types.entities.user import UserData
from app.types.services_result.admin import KillGhoulResult

from app.services import GhoulService

from app.database.repositories.common.user import UserRepository
from app.database.repositories.ghoul.ghoul import GhoulRepository

from app.utils.logger import admin_logger
from app.utils.truncate_text import truncate_text

class KillGhoulService:
    def __init__(
        self,
        user_repo: UserRepository,
        ghoul_repo: GhoulRepository,
        ghoul_service: GhoulService,
    ):
        self.user_repo = user_repo
        self.ghoul_repo = ghoul_repo
        self.ghoul_service = ghoul_service

    async def resolve_user(self, query: str | int) -> UserData:
        user = await self.user_repo.resolve(query)

        if not user:
            raise UserNotFoundError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Пользователь не найден: {query}."
            )

        return user

    async def kill(self, query: str | int, admin_id: int) -> KillGhoulResult:
        user = await self.user_repo.resolve(query)
        ghoul = await self.ghoul_repo.get(user.telegram_id)

        if not ghoul:
            raise ValueError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "У пользователя нет профиля гуля."
            )

        if ghoul.is_dead:
            return KillGhoulResult(
                user=user,
                already_dead=True,
                death_cause=ghoul.death_cause,
            )

        await self.ghoul_service.apply_death(user.telegram_id, DeathCause.ADMIN)

        admin_logger.info(f"[KILL] Admin kill ghoul | admin_id={admin_id} | user_id={user.telegram_id}")

        return KillGhoulResult(
            user=user,
            already_dead=False,
            death_cause=DeathCause.ADMIN.value
        )

    @staticmethod
    def fmt_result(result: KillGhoulResult) -> str:
        who = (
            f"<code>{result.user.telegram_id}</code> "
            f"({escape(truncate_text(result.user.name))})"
        )

        if result.already_dead:
            if result.death_cause == DeathCause.ADMIN.value:
                why = "уже убит администратором"
            elif result.death_cause == DeathCause.HUNGER.value:
                why = "уже сдох от голода"
            else:
                why = "уже мёртв"
            return (
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Пользователь {who} <b>{why}.</b>"
            )

        return (
            "<tg-emoji emoji-id=\"5294342418399783851\">💀</tg-emoji> "
            f"Пользователь {who} <b>убит администратором.</b>"
        )


