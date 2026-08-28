from dataclasses import dataclass
from datetime import datetime

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

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