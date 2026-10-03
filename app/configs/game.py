import random

from random import randint
from dataclasses import dataclass, field

from app.core.enums.daily_bonus import BonusReward
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
class DailyBonusConfig:
    cooldown: int = 24 * 60 * 60
    boxes: int = 5

    # Вес = относительный шанс. Шанс награды = вес / сумма весов доступных наград.
    weights: dict[BonusReward, int] = field(default_factory=lambda: {
        BonusReward.MONEY_SMALL: 220,
        BonusReward.MONEY_MEDIUM: 70,
        BonusReward.MONEY_JACKPOT: 8,
        BonusReward.MONEY_LOSS: 40,

        BonusReward.QUIZ_QUESTIONS: 70,
        BonusReward.QUIZ_RESET: 15,
        BonusReward.QUIZ_REWARD_BOOST: 30,

        BonusReward.RESET_SNAP: 20,
        BonusReward.RESET_COFFEE: 20,
        BonusReward.RESET_KAGUNE: 15,
        BonusReward.RESET_ALL: 5,

        BonusReward.FAST_SNAP: 30,
        BonusReward.FAST_COFFEE: 25,
        BonusReward.FAST_KAGUNE: 20,
        BonusReward.FAST_ALL: 6,

        BonusReward.PENALTY_SNAP: 15,
        BonusReward.PENALTY_COFFEE: 15,
        BonusReward.PENALTY_KAGUNE: 10,

        BonusReward.SNAP_COUNT: 40,
        BonusReward.COFFEE_COUNT: 35,
        BonusReward.KAGUNE_LEVEL: 20,
        BonusReward.STAT_UP: 8,

        BonusReward.KAGUNE_DISCOUNT: 25,
        BonusReward.STATS_DISCOUNT: 25,
        BonusReward.KAGUNE_PRICE_UP: 10,
        BonusReward.STATS_PRICE_UP: 10,

        BonusReward.EMPTY: 100,
    })

    # диапазоны «от и до»
    money_small: tuple[int, int] = (1000, 3000)
    money_medium: tuple[int, int] = (5000, 12000)
    money_jackpot: tuple[int, int] = (25000, 50000)
    money_loss: tuple[int, int] = (500, 3000)

    quiz_questions: tuple[int, int] = (1, 5)
    counts: tuple[int, int] = (1, 5)
    kagune_levels: tuple[int, int] = (1, 3)

    fast_multiplier: tuple[float, float] = (0.5, 0.8)  # кулдаун ×0.5–0.8
    discount_multiplier: tuple[float, float] = (0.7, 0.9)  # цена −10…−30%
    price_up_multiplier: tuple[float, float] = (1.1, 1.2)  # цена +10…+20%
    quiz_boost_multiplier: tuple[float, float] = (1.5, 2.0)

    effect_duration: tuple[int, int] = (2 * 60 * 60, 12 * 60 * 60)
    penalty_duration: tuple[int, int] = (10 * 60, 60 * 60)

    def random_reward(self, allowed: set[BonusReward]) -> BonusReward:
        rewards = [reward for reward in self.weights if reward in allowed]

        return random.choices(
            population=rewards,
            weights=[self.weights[reward] for reward in rewards],
            k=1
        )[0]

@dataclass(slots=True, frozen=True)
class KaguneConfig:
    start_price: int = 500
    price_multiplier: float = 1.05
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
class TransferConfig:
    min_amount: int = 100
    max_amount: int = 1000000

    min_sender_account_age_days: int = 3
    max_received_per_day: int = 15

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
    transfer: TransferConfig = field(default_factory=TransferConfig)
    daily_bonus: DailyBonusConfig = field(default_factory=DailyBonusConfig)

game_cfg = GameConfig()