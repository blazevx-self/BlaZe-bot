from math import floor
from typing import Literal

from app.core.constants.game.stats import STAT_LIMITS, UNLOCK_LEVELS
from app.core.enums import ResultStatus

from app.types.services_result.ghoul import UpgradeCalcResult
from app.configs.game import game_cfg


UpgradeAmount = Literal[1, 3, 5]


def calculate_price(current_stat: int, amount: int) -> int:
    """Расчёт стоимости улучшений с учётом экспоненциального роста"""

    price_cfg = game_cfg.stats_price
    base_price = price_cfg.base_price
    multiplier = price_cfg.price_multiplier

    total_price = 0
    temp_stat = current_stat

    for _ in range(amount):
        total_price += floor(base_price * (multiplier ** temp_stat))
        temp_stat += 1

    return total_price


def can_upgrade_amount(current_stat: int, amount: UpgradeAmount) -> bool:
    """Проверка: открыта ли кнопок апа (+3 или +5) на текущем уровне стата"""

    required_level = UNLOCK_LEVELS[amount]
    return current_stat >= required_level


def calculate_upgrade(
    stat: str,
    current_stat: int,
    amount: UpgradeAmount,
    money: int
) -> UpgradeCalcResult:
    """Проверка лимитов, расчёт финальной стоимости и валидация баланса"""

    if stat not in STAT_LIMITS:
        return UpgradeCalcResult(status=ResultStatus.INVALID_STAT)

    if amount not in (1, 3, 5):
        return UpgradeCalcResult(status=ResultStatus.INVALID_AMOUNT)

    stat_limit = STAT_LIMITS[stat]

    if not can_upgrade_amount(current_stat, amount):
        return UpgradeCalcResult(status=ResultStatus.LOCKED)

    if current_stat >= stat_limit:
        return UpgradeCalcResult(status=ResultStatus.MAXED)

    remaining_points = stat_limit - current_stat
    upgrade_amount = min(int(amount), remaining_points)

    price = calculate_price(
        current_stat=current_stat,
        amount=upgrade_amount
    )

    if money < price:
        return UpgradeCalcResult(
            status=ResultStatus.NOT_ENOUGH_MONEY,
            missing=price - money
        )

    return UpgradeCalcResult(
        status=ResultStatus.SUCCESS,
        price=price,
        upgrade_amount=upgrade_amount,
        new_value=current_stat + upgrade_amount
    )
