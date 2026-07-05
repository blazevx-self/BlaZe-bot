import random
from dataclasses import dataclass, field

@dataclass(slots=True, frozen=True)
class RankWeights:
    money: float = 0.01
    clicks: float = 1.0
    coffee: int = 30
    kagune_lvl: int = 300
    strength: int = 25
    agility: int = 25
    speed: int = 25
    hp: int = 20
    regen: int = 25

@dataclass(slots=True, frozen=True)
class RankConfig:
    weights: RankWeights = field(default_factory=RankWeights)

    ghoul_ranks: dict[int, str] = field(default_factory=lambda: {
        5: "E",
        10: "D",
        20: "C",
        35: "B",
        60: "A",
        100: "S",
        200: "SS",
        99999: "SSS"
    })

    statuses: dict[int, str] = field(default_factory=lambda: {
        200: "Гуль одиночка",
        1000: "Работник «Антейку»",
        5000: "Член «Аогири»",
        15000: "Каннибал-потрошитель",
        35000: "Сколопендра",
        60000: "Неудержимый гуль",
        100000: "Бедствие всего района",
        145000: "Глава Токио",
        250000: "Повелитель",
        300000: "Чёрный бог смерти",
        325000: "Одноглазый король",
        400000: "ЛЕХЕНДА 👑",
    })

@dataclass(slots=True, frozen=True)
class KaguneConfig:
    start_price: int = 150
    price_multiplier: float = 1.07
    cooldown: int = 900

    types_chance: dict[str, int] = field(default_factory=lambda: {
        "Укаку": 45,
        "Коукаку": 40,
        "Ринкаку": 10,
        "Бикаку": 35,
    })

    def random_type(self) -> str:
        return random.choices(
            population=list(self.types_chance.keys()),
            weights=list(self.types_chance.values()),
            k=1,
        )[0]

@dataclass(slots=True, frozen=True)
class StatsPriceConfig:
    base_price: int = 120
    price_multiplier: float = 1.07

@dataclass(slots=True, frozen=True)
class CoffeeConfig:
    reward: tuple[int, int] = (1500, 2000)
    cooldown: int = 1800
    overdose_cooldown: int = 18000
    required_clicks: int = 100

@dataclass(slots=True, frozen=True)
class ClickConfig:
    reward: tuple[int, int] = (500, 1000)
    cooldown: int = 600

@dataclass(slots=True, frozen=True)
class QuizConfig:
    day_limit: int = 15
    reward: tuple[int, int] = (1500, 2500)
    reset_time: str = "00:00"

@dataclass(slots=True, frozen=True)
class EconomyConfig:
    ranks: RankConfig = field(default_factory=RankConfig)
    kagune: KaguneConfig = field(default_factory=KaguneConfig)
    stats_price: StatsPriceConfig = field(default_factory=StatsPriceConfig)
    coffee: CoffeeConfig = field(default_factory=CoffeeConfig)
    click: ClickConfig = field(default_factory=ClickConfig)
    quiz: QuizConfig = field(default_factory=QuizConfig)

game_cfg = EconomyConfig()