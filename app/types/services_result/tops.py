from dataclasses import dataclass

from app.core.enums import ResultStatus

from app.types.entities.ghoul import GhoulData
from app.types.entities.user import UserData

@dataclass
class TopUser:
    user: UserData
    ghoul: GhoulData | None = None

@dataclass
class TopResult:
    status: ResultStatus
    user: UserData
    top_user: list[TopUser]
    ghoul: GhoulData | None
    rank: int = 0