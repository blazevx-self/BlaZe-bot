import random

from random import randint
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class StartConfig:
    bonus_amount: int = 10000
    channel_id: int = -1003884750303
    guide_link: str = "https://t.me/+ChhN0j9eYMI3ODBi"
    telegraph_link: str = "https://telegra.ph/BlaZe--Bot--help-08-14"
    channel_link: str = "https://t.me/+H67pSJL-qYU5Y2Qy"


@dataclass(slots=True, frozen=True)
class ProfileStatusWeights:
    money: float = 0.01
    days_in_project: float = 15.0


@dataclass(slots=True, frozen=True)
class ProfileStatusConfig:
    weights: ProfileStatusWeights = field(default_factory=ProfileStatusWeights)
    statuses: dict[int, str] = field(default_factory=lambda: {
        100: "Первый шаг",
        250: "Осваивающийся",
        500: "Знакомый",
        1000: "Свой человек",
        5000: "Постоянный участник",
        15000: "Активист",
        35000: "Уважаемый участник",
        60000: "Влиятельный",
        100000: "Настоящий олд",
        145000: "Почётный участник",
        250000: "Икона сообщества",
        300000: "Живая легенда",
        325000: "Опора сообщества",
        400000: "Легенда проекта 👑",
    })


@dataclass(slots=True, frozen=True)
class KaguneConfig:
    start_price: int = 500
    price_multiplier: float = 1.05
    cooldown: int = 15 * 60

    types_chance: dict[str, int] = field(default_factory=lambda: {
        "Укаку": 45,
        "Коукаку": 30,
        "Ринкаку": 15,
        "Бикаку": 20,
    })

    def random_type(self) -> str:
        return random.choices(
            population=list(self.types_chance.keys()),
            weights=list(self.types_chance.values()),
            k=1,
        )[0]


@dataclass(slots=True, frozen=True)
class StatsPriceConfig:
    base_price: int = 250
    price_multiplier: float = 1.04


@dataclass(slots=True, frozen=True)
class CoffeeConfig:
    min_award: int = 1200
    max_award: int = 1800
    cooldown: int = 30 * 60
    overdose_cooldown: int = 5 * 60 * 60
    required_snap: int = 100

    @property
    def award(self) -> int:
        return randint(self.min_award, self.max_award)


@dataclass(slots=True, frozen=True)
class SnapConfig:
    min_award: int = 500
    max_award: int = 1000
    cooldown: int = 10 * 60

    @property
    def award(self) -> int:
        return randint(self.min_award, self.max_award)


@dataclass(slots=True, frozen=True)
class QuizConfig:
    day_limit: int = 15
    min_award: int = 1800
    max_award: int = 3000
    reset_time: str = "00:00"

    @property
    def award(self) -> int:
        return randint(self.min_award, self.max_award)


@dataclass(slots=True, frozen=True)
class TopsConfig:
    money_limit: int = 15
    snap_limit: int = 20
    kagune_limit: int = 10

    def get_limit(self, top_type: str) -> int:
        return {
            "money": self.money_limit,
            "snap": self.snap_limit,
            "kagune": self.kagune_limit,
        }[top_type]


@dataclass(slots=True, frozen=True)
class WordleConfig:
    min_award: int = 3000
    max_award: int = 5000
    
    @property
    def award(self) -> int:
        return randint(self.min_award, self.max_award)


@dataclass(slots=True, frozen=True)
class EconomyConfig:
    start: StartConfig = field(default_factory=StartConfig)
    profile_statuses: ProfileStatusConfig = field(default_factory=ProfileStatusConfig)
    kagune: KaguneConfig = field(default_factory=KaguneConfig)
    stats_price: StatsPriceConfig = field(default_factory=StatsPriceConfig)
    coffee: CoffeeConfig = field(default_factory=CoffeeConfig)
    snap: SnapConfig = field(default_factory=SnapConfig)
    quiz: QuizConfig = field(default_factory=QuizConfig)
    tops: TopsConfig = field(default_factory=TopsConfig)
    wordle: WordleConfig = field(default_factory=WordleConfig)

game_cfg = EconomyConfig()