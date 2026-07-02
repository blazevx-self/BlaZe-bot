from typing import Literal

from app.configs.yaml import cfg

from app.core.templates.ghoul.stats_template import stats_text
from app.core.constants.game.stats import STAT_NAMES
from app.core.enums import ResultStatus
from app.types.services_types.ghoul import StatsResult

from app.database.repositories.ghouls_repository import ghouls_repository
from app.database.repositories.users_repository import user_repository

from app.bot.keyboards.ghoul.stats_keyboard import builds_stats_keyboard
from app.utils.calculate_stats import calculate_upgrade

UpgradeAmount = Literal[1, 3, 5]

# noinspection PyMethodMayBeStatic
class StatsService:
    """Сервис управления характеристиками гуля.

    Отвечает за отображения меню характеристик и обработку их улучшения.
    """

    async def get_stats_menu(self, user: dict) -> StatsResult:
        """Формирует меню характеристик игрока.

        Получает текущие характеристики пользователя и возвращает текст вместе с клавиатурой
        """

        stats = await ghouls_repository.get_stats(user["user_id"])

        if not stats:
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

    async def process_stats_upgrade(
            self,
            user: dict,
            stat: str,
            amount: UpgradeAmount
    ) -> StatsResult:
        """Обрабатывает улучшения выбранной характеристики.

        Проверяет возможность прокачки, рассчитывает стоимость,
        обновляет данные в базе и возвращает новый интерфейс.
        """

        user_id = user['user_id']
        current_user_db = await user_repository.get_user_by_id(user_id)

        if not current_user_db:
            return StatsResult(
                status=ResultStatus.NOT_FOUND,
                notification="Пользователь не найден"
            )

        stats = await ghouls_repository.get_stats(user_id)

        if not stats:
           return StatsResult(
               status=ResultStatus.NOT_FOUND,
               notification="Статы не найдены"
           )

        current_stat = stats[stat]

        calc_result = calculate_upgrade(
            stat=stat,
            current_stat=current_stat,
            amount=amount,
            money=current_user_db['money']
        )

        if calc_result.status != ResultStatus.SUCCESS:
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
            return StatsResult(
                status=ResultStatus.NOT_ENOUGH_MONEY,
                notification="Ошибка транзакции балика"
            )

        updated_user = await user_repository.get_user_by_id(user_id)
        updated_stats = await ghouls_repository.get_stats(user_id)

        return StatsResult(
            status=ResultStatus.SUCCESS,
            text=stats_text(updated_user, updated_stats),
            keyboard=builds_stats_keyboard(updated_stats),
            notification=f"{STAT_NAMES[stat]} улучшен на +{calc_result.upgrade_amount}"
        )

stats_service = StatsService()