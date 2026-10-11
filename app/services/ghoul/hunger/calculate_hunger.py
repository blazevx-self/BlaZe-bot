from math import floor
from datetime import datetime, timezone

from app.configs.game import game_cfg
from app.core.enums.hunger import HungerTier

def current_hunger(hunger: int, updated_at: datetime, now: datetime) -> int:
    """Текущий голод: значение из базы минус то, что истекло с момента записи"""

    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)

    elapsed_hours = max(0.0, (now - updated_at).total_seconds() / 3600)
    lost = floor(elapsed_hours * game_cfg.hunger.per_hour)

    return max(0, hunger - lost)

def hunger_tier(hunger: int) -> HungerTier:
    """Тир голода по процентам: идём по порогам сверху вниз"""

    for threshold, tier in game_cfg.hunger.tiers:
        if hunger >= threshold:
            return tier

    return HungerTier.DEADLY

def hours_until_starved(hunger: int) -> float:
    """Через сколько часов голод дойдёт до 0, если не есть"""
    return hunger / game_cfg.hunger.per_hour

def restore_hunger(hunger: int, amount: int) -> int:
    """Прибавить голод после еды, не выше максимума"""
    return min(game_cfg.hunger.max_hunger, hunger + amount)

def next_threshold(hunger: int) -> int | None:
    for value in game_cfg.hunger.thresholds:
        if hunger > value:
            return value

    return None