from datetime import datetime, timedelta, UTC

from app.configs.settings import settings
from app.core.exceptions.user import UserNotFoundError

from app.types.entities.user import UserData
from app.types.services_result.admin import BanResult

from app.database.repositories.common.user import UserRepository
from app.utils.logger import admin_logger

class BanService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    @staticmethod
    def _parse_duration(value: str) -> datetime | None:
        """'7d', '24h', '30m' -> datetime. Всё остальное -> None (перманентно)."""
        
        if not value:
            return None
        
        units = {"m": "minutes", "h": "hours", "d": "days"}

        if len(value) >= 2 and value[-1] in units and value[:-1].isdigit():
            return datetime.now(UTC) + timedelta(**{units[value[-1]]: int(value[:-1])})

        return None

    async def _resolve_user(self, query: str | int) -> UserData:
        user = await self.user_repo.resolve(query)

        if not user:
            raise UserNotFoundError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Пользователь не найден: {query}."
            )

        return user

    async def ban(
        self,
        query: str | int,
        duration: str | None = None,
        reason: str | None = None,
        admin_id: int | None = None
    ) -> BanResult:
        user = await self._resolve_user(query)

        if user.is_banned:
            raise ValueError(
                "<tg-emoji emoji-id=\"5258318620722733379\">🚫</tg-emoji> "
                "Пользователь уже забанен."
            )

        if user.telegram_id in settings.ADMIN_IDS:
            raise ValueError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя забанить главного администратора бота."
            )

        banned_until = self._parse_duration(duration)

        if duration and banned_until is None:
            reason = f"{duration} {reason or ''}".strip()

        await self.user_repo.ban(
            telegram_id=user.telegram_id,
            reason=reason,
            banned_until=banned_until
        )

        admin_logger.info(
            f"[BAN] User banned | user_id: {user.telegram_id} | admin_id: {admin_id} "
            f"name={user.name} "
            f"| until={banned_until} | reason={reason!r}"
        )

        return BanResult(
            user=user,
            banned_until=banned_until,
            reason=reason
        )

    async def unban(self, query: str | int) -> UserData:
        user = await self._resolve_user(query)

        if not user.is_banned:
            raise ValueError(
                "<tg-emoji emoji-id=\"5386470514871003633\">☕️</tg-emoji>"
                "Пользователь не забанен."
            )

        await self.user_repo.unban(telegram_id=user.telegram_id)

        return user

    @staticmethod
    def fmt_ban_result(result: BanResult) -> str:
        until = (
            f"до {result.banned_until.strftime('%d.%m.%Y %H:%M')}"
            if result.banned_until
            else "навсегда"
        )

        return (
            "<tg-emoji emoji-id=\"5258318620722733379\">🚫</tg-emoji> "
            f"Пользователь <code>{result.user.telegram_id}</code> "
            f"({result.user.name}) <b>заблокирован {until}.</b>\n\n"
            "<tg-emoji emoji-id=\"5778299625370817409\">📝</tg-emoji> "
            f"<b>Причина:</b> <i>{result.reason or 'Не указана'}</i>"
        )

    @staticmethod
    def fmt_unban_result(user: UserData) -> str:
        return (
            "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
            f"Пользователь <code>{user.telegram_id}</code> "
            f"({user.name}) <b>разблокирован.</b>\n\n"
        )