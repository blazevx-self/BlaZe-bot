from dataclasses import dataclass
from app.core.enums import ResultStatus

@dataclass
class TopBalResult:
    status: ResultStatus
    top_user: list[dict] | None = None
    rank: int | None = None
    user: dict | None = None

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