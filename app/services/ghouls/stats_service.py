from typing import Literal

from app.config import cfg

from app.core.templates.ghoul.stats_template import stats_text
from app.core.constants.game import STAT_NAMES
from app.core.responses import success, error

from app.database.repositories.ghouls_repository import ghouls_repository
from app.database.repositories.users_repository import user_repository

from app.bot.keyboards.ghoul.stats_keyboard import builds_stats_keyboard
from app.utils.calculate_stats import calculate_upgrade

UpgradeAmount = Literal[1, 3, 5]

# noinspection PyMethodMayBeStatic
class StatsService:
    async def get_stats_menu(self, user: dict) -> dict:
        stats = await ghouls_repository.get_stats(user["user_id"])

        if not stats:
            return error("Статы не найдены")

        text = stats_text(user, stats)

        return success(
            text=text,
            keyboard=builds_stats_keyboard(stats)
        )

    async def process_stats_upgrade(
            self,
            user: dict,
            stat: str,
            amount: UpgradeAmount
    ) -> dict:

        user_id = user['user_id']

        current_user_db = await user_repository.get_user_by_id(user_id)
        if not current_user_db:
            return error("Пользователь не найден")

        stats = await ghouls_repository.get_stats(user_id)

        if not stats:
           return error("Статы не найдены")

        current_stat = stats[stat]

        result = calculate_upgrade(
            stat=stat,
            current_stat=current_stat,
            amount=amount,
            money=current_user_db['money']
        )

        if not result['success']:
            reason = result["reason"]

            return error(
                notification=cfg['message']['notifications'].get(
                    reason,
                    "Ошибка прокачки статов"
                )
            )

        updated = await ghouls_repository.upgrade_stat(
            user_id=user_id,
            stat=stat,
            amount=result['upgrade_amount'],
            price=result['price']
        )

        if not updated:
            return error("Недостаточно BC на балике (Ошибка транзакции)")

        updated_user = await user_repository.get_user_by_id(user_id)
        updated_stats = await ghouls_repository.get_stats(user_id)

        return success(
            text=stats_text(updated_user, updated_stats),
            keyboard=builds_stats_keyboard(updated_stats),
            notification=f"{STAT_NAMES[stat]} улучшен на +{result['upgrade_amount']}",
            show_alert=False
        )

stats_service = StatsService()