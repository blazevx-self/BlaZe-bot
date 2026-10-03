import time

from app.core.enums.daily_bonus import EffectKey
from app.types.entities.user import UserData

def effect_multiplier(user: UserData, key: EffectKey) -> float:
    """Множитель активного эффекта (1.0 — если эффекта нет или он истёк)."""

    effect = user.effects.get(key)

    if not effect or effect["until"] <= time.time():
        return 1.0

    return effect["mult"]

def apply_effect(user: UserData, key: EffectKey, value: int) -> int:
    """Применяет эффект к значению (кулдаун, цена, награда)."""
    return max(1, round(value * effect_multiplier(user, key)))