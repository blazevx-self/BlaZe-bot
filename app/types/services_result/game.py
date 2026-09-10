from dataclasses import dataclass, field

from app.core.constants.game.wordle import MAX_ATTEMPTS
from app.core.enums import ResultStatus
from app.core.enums.letterstate import LetterState
from app.core.enums.lottery import LotteryColor

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.database.models.quiz import QuizOrm

@dataclass
class QuizStartResult:
    status: ResultStatus
    question: QuizOrm | None = None
    left: int | None = None

@dataclass
class QuizAnswerResult:
    status: ResultStatus
    text: str | None = None

@dataclass(slots=True, frozen=True)
class GuessResult:
    word: str
    states: list[LetterState]

    @property
    def is_win(self) -> bool:
        return all(state == LetterState.CORRECT for state in self.states)

    def to_emoji(self) -> str:
        emojis = {
            LetterState.CORRECT: "🟩",
            LetterState.PRESENT: "🟨",
            LetterState.ABSENT: "⬛",
        }

        return "".join(emojis[state] for state in self.states)

@dataclass(slots=True)
class WordleSession:
    target_word: str
    guesses: list[GuessResult] = field(default_factory=list)
    board_message_id: int | None = None

    @property
    def attempts_used(self) -> int:
        return len(self.guesses)

    @property
    def attempts_left(self) -> int:
        return MAX_ATTEMPTS - len(self.guesses)

    @property
    def is_win(self) -> bool:
        return bool(self.guesses) and self.guesses[-1].is_win

    @property
    def is_game_over(self) -> bool:
        return self.is_win or self.attempts_used >= MAX_ATTEMPTS

@dataclass
class WordleResult:
    image: bytes
    guess: GuessResult
    attempts_used: int
    attempts_left: int
    is_win: bool
    is_game_over: bool
    target_word: str | None = None
    board_message_id: int | None = None
    earned: int = 0

@dataclass(slots=True, frozen=True)
class LotteryResult:
    ghoul: GhoulData
    user: UserData
    bet_amount: int
    chosen_color: LotteryColor
    winning_color: LotteryColor
    is_won: bool
    earned: int
    video: bytes
    text: str | None = None