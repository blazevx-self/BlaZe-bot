from dataclasses import dataclass
from app.core.enums import ResultStatus

@dataclass
class QuizStartResult:
    status: ResultStatus
    question: dict | None = None
    left: int | None = None

@dataclass
class QuizAnswerResult:
    status: ResultStatus
    text: str | None = None
    new_money: int | None = None
