from datetime import datetime, timedelta, timezone

from app.configs.settings import settings

from app.types.entities import UserData
from app.types.services_result.admin import BanResult

from app.database.repositories.users_repository import user_repository

class BanService:
    """Сервис управления банами пользователей."""
    
    @staticmethod
    def _parse_duration(value: str) -> datetime | None:
        """'7d', '24h', '30m' -> datetime. Всё остальное -> None (перманентно)."""
        
        if not value:
            return None
        
        units = {"m": "minutes", "h": "hours", "d": "days"}

        if len(value) >= 2 and value[-1] in units and value[:-1].isdigit():
            return datetime.now(timezone.utc) + timedelta(**{units[value[-1]]: int(value[:-1])})

        return None


    @staticmethod
    async def _resolve_user(query: str | int) -> UserData:
        user = await user_repository.resolve(query)

        if not user:
            raise ValueError(f"⚠️ Пользователь не найден: {query}")

        return user


    async def ban(
        self,
        query: str | int,
        duration: str | None = None,
        reason: str | None = None
    ) -> BanResult:
        """Блокирует пользователя на указанный срок или навсегда."""

        user = await self._resolve_user(query)

        if user.is_banned:
            raise ValueError("🚫 Пользователь уже забанен.")


        if user.user_id == settings.ADMIN_ID:
            raise ValueError("⚠️ Нельзя забанить владельца бота.")

        banned_until = self._parse_duration(duration)

        if duration and banned_until is None:
            reason = f"{duration} {reason or ''}".strip()

        await user_repository.ban(user.user_id, reason, banned_until)

        return BanResult(
            user=user,
            banned_until=banned_until,
            reason=reason
        )


    async def unban(self, query: str | int) -> UserData:
        """Снимает бан с пользователя."""

        user = await self._resolve_user(query)

        if not user.is_banned:
            raise ValueError("☕️ Пользователь не забанен.")

        await user_repository.unban(user.user_id)

        return user


    @staticmethod
    def fmt_ban_result(result: BanResult) -> str:
        until = (
            f"до {result.banned_until.strftime('%d.%m.%Y %H:%M')}"
            if result.banned_until
            else "навсегда"
        )

        return (
            f"🚫 Пользователь <code>{result.user.user_id}</code> "
            f"({result.user.name}) <b>заблокирован {until}.</b>\n\n"
            f"<b>Причина:</b> <i>{result.reason or 'Не указана'}</i>"
        )


    @staticmethod
    def fmt_unban_result(user: UserData,) -> str:
        return (
        f"✅ Пользователь <code>{user.user_id}</code> "
        f"({user.name}) <b>разблокирован.</b>\n\n"
    )

ban_service = BanService()