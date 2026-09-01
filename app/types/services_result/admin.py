from dataclasses import dataclass
from datetime import datetime

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.database.models.user import UserOrm
from app.database.models.ghoul import GhoulOrm

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
    target: UserOrm | GhoulOrm
    field: str
    value: int
    is_ghoul_field: bool