from typing import Literal

from app.configs.yaml import cfg

from app.core.templates.ghoul.stats_template import stats_text
from app.core.constants.game.stats import STAT_NAMES
from app.core.enums import ResultStatus

from app.types.services_result.ghoul import StatsResult
from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.database.repositories.ghouls_repository import GhoulRepository
from app.database.repositories.users_repository import UserRepository

from app.services.ghouls.stats.calculate_stats_service import calculate_upgrade
from app.bot.keyboards.ghoul.stats_keyboard import builds_stats_keyboard

from app.utils.logger import stats_logger

UpgradeAmount = Literal[1, 3, 5]

class StatsService:
    def __init__(self, ghoul_repo: GhoulRepository, user_repo: UserRepository):
        self.ghoul_repo = ghoul_repo
        self.user_repo = user_repo

    @staticmethod
    async def get_stats_menu(user: UserData, ghoul: GhoulData | None) -> StatsResult:
        """Формирует меню характеристик игрока.

        Получает текущие характеристики пользователя и возвращает текст вместе с клавиатурой
        """
        if ghoul is None:
            stats_logger.warning(f"[STATS] Stats not found | user_id={user.telegram_id}")

            return StatsResult(
                status=ResultStatus.NOT_FOUND,
                notification="Статы не найдены"
            )

        text = stats_text(user, ghoul)

        return StatsResult(
            status=ResultStatus.SUCCESS,
            text=text,
            keyboard=builds_stats_keyboard(ghoul)
        )

    async def stats_upgrade(
            self,
            user: UserData,
            ghoul: GhoulData | None,
            stat: str,
            amount: UpgradeAmount
    ) -> StatsResult:
        """Обрабатывает улучшения выбранной характеристики.

        Проверяет возможность прокачки, рассчитывает стоимость,
        обновляет данные в базе и возвращает новый интерфейс.
        """

        user_id = user.telegram_id

        if ghoul is None:
            stats_logger.warning(f"[STATS] Stats not found | user_id={user_id}")

            return StatsResult(
                status=ResultStatus.NOT_FOUND,
                notification="Статы не найдены"
            )

        current_stat = getattr(ghoul, stat)

        calc_result = calculate_upgrade(
            stat=stat,
            current_stat=current_stat,
            amount=amount,
            money=user.money
        )

        if calc_result.status != ResultStatus.SUCCESS:
            stats_logger.debug(
             f"[STATS] Upgrade denied | user_id={user_id} | "
             f"stat={stat} | amount={amount} | reason={calc_result.status.value}"
            )

            notification=cfg['message']['stats']['notifications'].get(
                calc_result.status,
                "Ошибка прокачки статов"
            )

            return StatsResult(
                status=ResultStatus.ERROR,
                notification=notification
            )

        try:
            await self.ghoul_repo.upgrade_stat(
                telegram_id=user_id,
                stat=stat,
                amount=calc_result.upgrade_amount,
            )

            new_balance = await self.user_repo.change_money(
                telegram_id=user_id,
                amount=-calc_result.price
            )
        except Exception:
            stats_logger.exception(
                f"[STATS] Stats upgrade failed | user_id={user_id} | "
                f"stat={stat} | amount={calc_result.upgrade_amount} | price={calc_result.price}"
            )
            raise

        setattr(ghoul, stat, calc_result.new_value)
        user.money = new_balance

        stats_logger.info(
            f"[STATS] Upgrade completed | user_id={user_id} | stat={stat} | "
            f"old={current_stat} | new={calc_result.new_value} | "
            f"amount={calc_result.upgrade_amount} | price={calc_result.price}"
        )

        return StatsResult(
            status=ResultStatus.SUCCESS,
            text=stats_text(user, ghoul),
            keyboard=builds_stats_keyboard(ghoul),
            notification=f"{STAT_NAMES[stat]} улучшен на +{calc_result.upgrade_amount}"
        )