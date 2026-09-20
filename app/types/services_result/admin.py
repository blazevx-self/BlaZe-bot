from dataclasses import dataclass
from datetime import datetime

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

#from app.database.models.user import UserOrm
#from app.database.models.ghoul import GhoulOrm

from typing import Any

@dataclass
class BanResult:
    user: UserData
    banned_until: datetime | None = None
    reason: str | None = None

@dataclass
class ModifyBalanceResult:
    user: UserData
    amount: int
    balance: int
    currency: str = "BC"

@dataclass
class AdminUserProfileResult:
    user: UserData
    ghoul: GhoulData | None = None

@dataclass
class FieldEditResult:
    target: Any | None
    field: str
    value: int
    is_ghoul_field: bool

@dataclass
class ResetResult:
    telegram_id: int
    user_deleted: bool
    ghoul_deleted: bool

@dataclass
class BroadcastResult:
    total: int
    success: int
    failed: int