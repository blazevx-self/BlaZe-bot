from dataclasses import dataclass

from app.core.enums import ResultStatus

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