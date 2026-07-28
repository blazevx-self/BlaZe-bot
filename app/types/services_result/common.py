from dataclasses import dataclass
from app.core.enums import ResultStatus

@dataclass
class StartResult:
    status: ResultStatus
    text: str | None = None
    new_money: int | None = None
    is_subscribed: bool = None

@dataclass
class ProfileResult:
    status: ResultStatus
    text: str | None = None