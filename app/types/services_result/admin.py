from dataclasses import dataclass
from datetime import datetime

from app.types.entities import UserData

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