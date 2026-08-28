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