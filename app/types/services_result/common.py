from dataclasses import dataclass, field

from pathlib import Path
from datetime import datetime

from app.core.enums import ResultStatus
from app.core.enums.daily_bonus import BonusReward

@dataclass
class StartResult:
    status: ResultStatus
    text: str | None = None

@dataclass
class ProfileResult:
    status: ResultStatus
    text: str | None = None

@dataclass
class TransferResult:
    status: ResultStatus
    text: str | None = None
    amount: int | None = None
    receiver_id: int | None = None
    sender_balance: int | None = None
    receiver_balance: int | None = None

@dataclass
class WikipediaDescriptionResult:
    text: str

@dataclass
class DailyBonusResult:
    status: ResultStatus
    text: str | None = None
    reward: BonusReward | None = None
    others: list[BonusReward] = field
    remaining: int = 0

@dataclass
class AnimeClipResult:
    status: ResultStatus
    path: Path | None = None
    limit: int = 0

@dataclass
class ProposeResult:
    proposal_id: int
    expires_at: datetime

@dataclass
class ConsentResult:
    stage: str
    initiator_ok: bool
    target_ok: bool
    done: bool = False

@dataclass
class DivorceResult:
    heir_id: int | None
    inherited: int
    taken: int = 0