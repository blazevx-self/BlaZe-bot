from typing import Literal
from aiosqlite import Row

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from app.core.constants.game.stats import STATS_KEYBOARD
from app.services.calculate_stats_service import can_upgrade_amount


UpgradeAmount = Literal[1, 3, 5]
UPGRADE_AMOUNTS: tuple[UpgradeAmount, ...] = (1, 3, 5)


def builds_stats_keyboard(stats: Row) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for stat, emoji in STATS_KEYBOARD.items():
        current_stat = stats[stat]

        row = []

        for amount in UPGRADE_AMOUNTS:
            unlocked = can_upgrade_amount(
                current_stat=current_stat,
                amount=amount,
            )

            if unlocked:
                text = f"{emoji} +{amount}"
                callback = f"stat:{stat}:{amount}"

            else:
                text = f"🔒 +{amount}"
                callback = "locked"

            row.append(
                {
                 "text": text,
                 "callback_data": callback,
                }
            )

        for button in row:
            builder.button(**button)

    builder.adjust(3)

    return builder.as_markup()