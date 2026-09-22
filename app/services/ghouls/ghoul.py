import random

from app.configs.game import game_cfg
from app.configs.yaml_loader import cfg

from app.core.constants.game.stats import POWER_FIELDS
from app.core.constants.game.kagune import KAGUNE_MULTIPLIER
from app.core.constants.game.ranks import DANGER_RANKS

from app.types.entities.ghoul import GhoulData

from app.database.repositories.ghoul import GhoulRepository

class GhoulService:
    """Общий сервис игровых механик гулей."""

    def __init__(self, ghoul_repo: GhoulRepository):
        self.ghoul_repo = ghoul_repo

    async def check_ghoul(
        self,
        user_id: int,
        cached_ghoul: GhoulData | None = None
    ) -> bool:
        """Проверяет, получил ли пользователь кагуне.

           Если GhoulData уже загружен из мидлвара -
           используем его.

           Иначе выполняем точечный запрос в БД."""

        if cached_ghoul is not None:
            return cached_ghoul.kagune_was_obtained

        ghoul = await self.ghoul_repo.get(user_id)

        return bool(ghoul and ghoul.kagune_was_obtained)

    @staticmethod
    def get_price_kagune(level: int) -> int:
        """Расчёт стоимости улучшения кагуне."""

        base = game_cfg.kagune.start_price
        multiplier = game_cfg.kagune.price_multiplier

        safe_level = min(level, 1000)
        return int(base * (multiplier ** (safe_level - 1)))

    @staticmethod
    def get_kagune_gif(kagune_type: str) -> str:
        """У каждого типа кагуне - своя гиф. (поиск без учёта регистра)."""

        gifs = cfg['assets']['kagune']['gifs']

        lookup = {str(k).strip().lower(): v for k, v in gifs.items()}
        key = (kagune_type or "").strip().lower()

        type_gifs = lookup.get(key)

        if not type_gifs:
            type_gifs = lookup.get("bikaku") or next(iter(gifs.values()))

        return random.choice(type_gifs)

    @staticmethod
    def get_kagune_obtained_gif() -> str:
        return cfg["assets"]["kagune"]["obtained_gif"]

    @staticmethod
    def calculate_power(ghoul: GhoulData) -> int:
        """Подсчёт боевой мощи.
          Складывает текущие статы из бд и уровень кагуне
        """

        base_power = sum(getattr(ghoul, field, 0) for field in POWER_FIELDS)
        base_power += ghoul.kagune_strength

        # Определяем тип кагуне.
        kagune_type = (ghoul.kagune_type or "").lower().strip()
        multiplier = KAGUNE_MULTIPLIER.get(kagune_type, 1.0)

        # Проверяем форму Какуджа (на будущее)
        if ghoul.is_kakuja:
            multiplier += 0.50

        return int(base_power * multiplier)

    @staticmethod
    def get_danger_rank(power: int) -> str:
        """Определение ранга угрозы
        на основе вычисленной суммарной мощи гуля
        """
        for limit, rank in DANGER_RANKS:
            if power < limit:
                return rank

        return "SSS+"