import random

from random import randint
from dataclasses import dataclass, field

from app.core.enums.lottery import LotteryColor

@dataclass(slots=True, frozen=True)
class StartConfig:
    bonus_amount: int = 10000
    channel_id: int = -1003884750303
    guide_link: str = "https://t.me/+ChhN0j9eYMI3ODBi"
    telegraph_link: str = "https://telegra.ph/BlaZe--Bot--Pomoshch-08-18-2"
    channel_link: str = "https://t.me/+H67pSJL-qYU5Y2Qy"

@dataclass(slots=True, frozen=True)
class ProfileStatusWeights:
    days_in_project: float = 15.0

@dataclass(slots=True, frozen=True)
class ProfileStatusConfig:
    weights: ProfileStatusWeights = field(default_factory=ProfileStatusWeights)
    statuses: dict[int, str] = field(default_factory=lambda: {
        1: "Первый шаг",
        3: "Осваивающийся",
        7: "Знакомый",
        14: "Свой человек",
        30: "Постоянный участник",
        60: "Активист",
        90: "Уважаемый участник",
        120: "Влиятельный",
        150: "Настоящий олд",
        180: "Почётный участник",
        240: "Икона сообщества",
        280: "Живая легенда",
        320: "Опора сообщества",
        365: "Легенда проекта",
    })

@dataclass(slots=True, frozen=True)
class KaguneConfig:
    start_price: int = 500
    price_multiplier: float = 1.06
    cooldown: int = 15 * 60

    types_chance: dict[str, int] = field(default_factory=lambda: {
        "Укаку": 45,
        "Коукаку": 30,
        "Ринкаку": 10,
        "Бикаку": 15,
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
    price_multiplier: float = 1.05

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
    coffee_limit: int = 20

    def get_limit(self, top_type: str) -> int:
        return {
            "money": self.money_limit,
            "snap": self.snap_limit,
            "kagune": self.kagune_limit,
            "coffee": self.coffee_limit,
        }[top_type]

@dataclass(slots=True, frozen=True)
class WordleConfig:
    min_award: int = 3000
    max_award: int = 5000
    
    @property
    def award(self) -> int:
        return randint(self.min_award, self.max_award)

@dataclass(slots=True, frozen=True)
class LotteryConfig:
    min_bet: int = 100
    max_bet: int = 1000000

    colors: dict[LotteryColor, tuple[float, int]] = field(
        default_factory=lambda: {
            LotteryColor.RED: (1.8, 28),
            LotteryColor.BLUE: (2.5, 22),
            LotteryColor.GREEN: (3.0, 20),
            LotteryColor.YELLOW: (5.0, 13),
            LotteryColor.WHITE: (10.0, 10),
        }
    )

    def get_multiplier(self, color: LotteryColor) -> float:
        return self.colors[color][0]

    def get_chance(self, color: LotteryColor) -> int:
        return self.colors[color][1]

    def get_random_color(self) -> LotteryColor:
        return random.choices(
            population=list(self.colors),
            weights=[chance for _, chance in self.colors.values()],
            k=1,
        )[0]

@dataclass(slots=True, frozen=True)
class GameConfig:
    start: StartConfig = field(default_factory=StartConfig)
    profile_statuses: ProfileStatusConfig = field(default_factory=ProfileStatusConfig)
    kagune: KaguneConfig = field(default_factory=KaguneConfig)
    stats_price: StatsPriceConfig = field(default_factory=StatsPriceConfig)
    coffee: CoffeeConfig = field(default_factory=CoffeeConfig)
    snap: SnapConfig = field(default_factory=SnapConfig)
    quiz: QuizConfig = field(default_factory=QuizConfig)
    tops: TopsConfig = field(default_factory=TopsConfig)
    wordle: WordleConfig = field(default_factory=WordleConfig)
    lottery: LotteryConfig = field(default_factory=LotteryConfig)

game_cfg = GameConfig()