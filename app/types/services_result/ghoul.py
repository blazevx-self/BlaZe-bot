from dataclasses import dataclass

from app.core.enums import ResultStatus
from aiogram.types import InlineKeyboardMarkup

@dataclass
class StatsResult:
    status: ResultStatus
    text: str | None = None
    keyboard: InlineKeyboardMarkup | None = None
    notification: str | None = None

@dataclass
class UpgradeCalcResult:
    status: ResultStatus
    price: int | None = None
    upgrade_amount: int | None = None
    new_value: int | None = None
    missing: int | None = None

@dataclass
class KaguneResult:
    status: ResultStatus
    text: str | None = None
    gif: str | None = None
    remaining: int | None = None
    missing: int | None = None
    kagune_type: str | None = None

@dataclass
class RaceProfileResult:
    status: ResultStatus
    text: str | None = None

@dataclass
class CoffeeResult:
    status: ResultStatus
    text: str | None = None
    gif: str | None = None

@dataclass
class SnapResult:
    status: ResultStatus
    text: str | None = None
    gif: str | None = None
    remaining: int | None = 0
    last_snap: int | None = None

