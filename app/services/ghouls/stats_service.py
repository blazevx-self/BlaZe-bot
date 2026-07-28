import asyncio
from typing import Literal

from app.configs.yaml import cfg

from app.core.templates.ghoul.stats_template import stats_text
from app.core.constants.game.stats import STAT_NAMES
from app.core.enums import ResultStatus

from app.types.services_result.ghoul import StatsResult
from app.types.entities import UserData

from app.database.repositories.ghouls_repository import ghouls_repository
from app.database.repositories.users_repository import user_repository

from app.services.calculate_stats_service import calculate_upgrade
from app.bot.keyboards.ghoul.stats_keyboard import builds_stats_keyboard

from app.utils.logger import stats_logger

UpgradeAmount = Literal[1, 3, 5]

class StatsService:
    """Сервис управления характеристиками гуля.

    Отвечает за отображения меню характеристик и обработку их улучшения.
    """

    @staticmethod
    async def get_stats_menu(user: UserData) -> StatsResult:
        """Формирует меню характеристик игрока.

        Получает текущие характеристики пользователя и возвращает текст вместе с клавиатурой
        """
        user_id = user.user_id

        stats = await ghouls_repository.get_stats(user.user_id)

        if not stats:
            stats_logger.warning(f"[STATS] Stats not found | user_id={user_id}")

            return StatsResult(
                status=ResultStatus.NOT_FOUND,
                notification="Статы не найдены"
            )

        text = stats_text(user, stats)

        return StatsResult(
            status=ResultStatus.SUCCESS,
            text=text,
            keyboard=builds_stats_keyboard(stats)
        )

    @staticmethod
    async def process_stats_upgrade(
            user: UserData,
            stat: str,
            amount: UpgradeAmount
    ) -> StatsResult:
        """Обрабатывает улучшения выбранной характеристики.

        Проверяет возможность прокачки, рассчитывает стоимость,
        обновляет данные в базе и возвращает новый интерфейс.
        """

        user_id = user.user_id
        current_user_db = await user_repository.get_user_by_id(user_id)

        if not current_user_db:
            stats_logger.warning(f"[STATS] User not found | user_id={user_id}")

            return StatsResult(
                status=ResultStatus.NOT_FOUND,
                notification="Пользователь не найден"
            )

        stats = await ghouls_repository.get_stats(user_id)

        if not stats:
           stats_logger.warning(f"[STATS] Stats not found | user_id={user_id}")

           return StatsResult(
               status=ResultStatus.NOT_FOUND,
               notification="Статы не найдены"
           )

        current_stat = stats[stat]

        calc_result = calculate_upgrade(
            stat=stat,
            current_stat=current_stat,
            amount=amount,
            money=current_user_db.money
        )

        if calc_result.status != ResultStatus.SUCCESS:
            stats_logger.debug(
             f"[STATS] Upgrade denied | user_id={user_id} | "
             f"stat={stat} | amount={amount} | reason={calc_result.status.value}"
            )

            notification=cfg['message']['notifications'].get(
                calc_result.status,
                "Ошибка прокачки статов"
            )

            return StatsResult(
                status=ResultStatus.ERROR,
                notification=notification
            )

        updated = await ghouls_repository.upgrade_stat(
            user_id=user_id,
            stat=stat,
            amount=calc_result.upgrade_amount,
            price=calc_result.price
        )

        if not updated:
            stats_logger.error(f"[STATS] Upgrade failed | user_id={user_id} | stat={stat} | reason=transaction_failed")

            return StatsResult(
                status=ResultStatus.NOT_ENOUGH_MONEY,
                notification="Ошибка транзакции балика"
            )

        stats_logger.info(
            f"[STATS] Upgrade completed | user_id={user_id} | stat={stat} | "
            f"old={current_stat} | new={calc_result.new_value} | "
            f"amount={calc_result.upgrade_amount} | price={calc_result.price}"
        )

        updated_user, updated_stats = await asyncio.gather(
            user_repository.get_user_by_id(user_id),
            ghouls_repository.get_stats(user_id)
        )

        return StatsResult(
            status=ResultStatus.SUCCESS,
            text=stats_text(updated_user, updated_stats),
            keyboard=builds_stats_keyboard(updated_stats),
            notification=f"{STAT_NAMES[stat]} улучшен на +{calc_result.upgrade_amount}"
        )

stats_service = StatsService()