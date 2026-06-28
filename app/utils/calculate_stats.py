from math import floor
from typing import Literal

from app.core.constants.game import STAT_LIMITS, UNLOCK_LEVELS
from app.config import cfg

UpgradeAmount = Literal[1, 3, 5]

def calculate_price(current_stat: int, amount: int) -> int:
    """Расчёт стоимости улучшений с учётом экспоненциального роста"""
    price_cfg = cfg['economy']['stats_price']
    base_price = price_cfg['base_price']
    multiplier = price_cfg['price_multiplier']

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
) -> dict:
    """Проверка лимитов, расчёт финальной стоимости и валидация баланса"""
    if stat not in STAT_LIMITS:
        return {
            "success": False,
            "reason": "invalid_stat"
        }

    if amount not in (1, 3, 5):
        return {
            "success": False,
            "reason": "invalid_amount"
        }

    stat_limit = STAT_LIMITS[stat]

    if not can_upgrade_amount(current_stat, amount):
        return {
            "success": False,
            "reason": "locked"
        }

    if current_stat >= stat_limit:
        return {
            "success": False,
            "reason": "maxed"
        }

    remaining_points = stat_limit - current_stat
    upgrade_amount = min(int(amount), remaining_points)

    price = calculate_price(
        current_stat=current_stat,
        amount=upgrade_amount
    )

    if money < price:
        return {
            "success": False,
            "reason": "not_enough_money",
            "missing": price - money
        }

    return {
        "success": True,
        "price": price,
        "upgrade_amount": upgrade_amount,
        "new_value": current_stat + upgrade_amount
    }