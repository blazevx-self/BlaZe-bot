from app.core.constants.game.stats import STAT_LIMITS
from app.core.exceptions.user import UserNotFoundError

from app.types.services_result.admin import AdminUserProfileResult

from app.database.repositories.user_repository import UserRepository
from app.database.repositories.ghoul_repository import GhoulRepository

from app.utils.format_num import format_num

class PlayerLookupService:
    def __init__(self, user_repo: UserRepository, ghoul_repo: GhoulRepository):
        self.user_repo = user_repo
        self.ghoul_repo = ghoul_repo

    async def get_profile(self, query: str | int) -> AdminUserProfileResult | None:
        user = await self.user_repo.resolve(query)

        if not user:
            raise UserNotFoundError(f"⚠️ Пользователь не найден: {query}")

        ghoul = await self.ghoul_repo.get(telegram_id=user.telegram_id)

        return AdminUserProfileResult(
            user=user,
            ghoul=ghoul
        )

    @staticmethod
    def fmt_profile_user(profile: AdminUserProfileResult) -> str:
        user = profile.user

        text = (
            f"👤 <b>Профиль пользователя</b>\n\n"
            
            f"ℹ️ <b>Информация о пользователе</b>\n"
            f"└ <b>ID:</b> <code>{user.telegram_id}</code>\n"
            f"└ <b>Имя</b>: <code>{user.name}</code>\n"
            f"└ <b>Username:</b> <code>@{user.username or '—'}</code>\n\n"
            
            f"💸 <b>Баланс:</b> <code>{format_num(user.money)} BlazeCoin</code>\n\n"
            
            f"🛡 <b>Состояние:</b>\n"
            f"└ <b>Статус:</b> <code>{'🚫 Заблокирован' if user.is_banned else '✅ Активен'}</code>\n"
            f"└ <b>Бонус за подписку:</b> <code>{'✅ Получен' if user.is_subscribed else '❌ Не получен'}</code>\n\n"
            
            f"📅 <b>Регистрация:</b> <code>{user.created_at.strftime('%d.%m.%Y %H:%M')}</code>"
        )

        if user.is_banned:
            until = (
                user.banned_until.strftime("%d.%m.%Y %H:%M UTC")
                if user.banned_until
                else "навсегда"
            )

            text += (
                f"\n\n🚫 <b>Блокировка</b>\n"
                f"└ <b>Причина:</b> <code>{user.ban_reason or 'не указана'}</code>\n"
                f"└ <b>Срок бана:</b> <code>{until}</code>"
            )

        if profile.ghoul:
            ghoul = profile.ghoul

            text += (
                f"\n\n🧬 <b>Гуль</b>\n"
                f"└ <b>Уровень:</b> <code>{format_num(ghoul.level)}</code>\n"
                f"└ <b>RC-клетки:</b> <code>{format_num(ghoul.rc_money)}</code>\n"
                f"└ <b>Сила:</b> <code>{format_num(ghoul.strength)}/{STAT_LIMITS['strength']}</code>\n"
                f"└ <b>Скорость:</b> <code>{format_num(ghoul.speed)}/{STAT_LIMITS['speed']}</code>\n"
                f"└ <b>Ловкость:</b> <code>{format_num(ghoul.dexterity)}/{STAT_LIMITS['dexterity']}</code>\n"
                f"└ <b>Здоровье:</b> <code>{format_num(ghoul.hp)}/{STAT_LIMITS['hp']}</code>\n"
                f"└ <b>Регенерация:</b> <code>{ghoul.regen}/{STAT_LIMITS['regen']}</code>\n"
                f"└ <b>Какуджа:</b> <code>{'✅ есть' if ghoul.is_kakuja else '❌ Нет'}</code>"
            )

            if ghoul.kagune_was_obtained:
                text += (
                    f"\n\n👁 <b>Кагуне</b>\n"
                    f"└ <b>Тип:</b> <code>{ghoul.kagune_type or '—'}</code>\n"
                    f"└ <b>Сила:</b> <code>{format_num(ghoul.kagune_strength)}</code>"
                )
            else:
                text += (
                    f"\n\n👁 <b>Кагуне</b>\n"
                    f"└ <b>Статус:</b> <code>❌ Не получен</code>"
                )

            text += (
                f"\n\n📊 <b>Статистика гуля</b>\n"
                f"└ <b>Сломано пальцев:</b> <code>{format_num(ghoul.snap_count)}</code>\n"
                f"└ <b>Выпито кофе:</b> <code>{format_num(ghoul.coffee_count)}</code>\n"
                f"└ <b>Съедено людей:</b> <code>{format_num(ghoul.eat_humans)}</code>\n"
                f"└ <b>Съедено гулей:</b> <code>{format_num(ghoul.eat_ghouls)}</code>"
            )

        return text