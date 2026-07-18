from dataclasses import dataclass

from app.core.enums import ResultStatus
from app.types.entities import UserData


@dataclass
class TopResult:
    status: ResultStatus
    user: UserData
    top_user: list[dict] | None = None
    rank: int = 0

