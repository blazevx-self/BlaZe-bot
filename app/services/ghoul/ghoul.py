from app.configs.game import game_cfg

from datetime import datetime, timezone

from app.core.constants.game.stats import POWER_FIELDS
from app.core.constants.game.kagune import KAGUNE_MULTIPLIER
from app.core.constants.game.ranks import DANGER_RANKS
from app.core.constants.media import KAGUNE_COLLECTIONS
from app.core.enums.media import MediaCollection
from app.core.enums.death_cause import DeathCause

from app.types.entities.ghoul import GhoulData

from app.database.repositories.ghoul.ghoul import GhoulRepository

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

    async def apply_death(self, user_id: int, cause: DeathCause) -> None:
        ghoul = await self.ghoul_repo.get(user_id)

        if ghoul is None or ghoul.is_dead:
            return

        await self.ghoul_repo.change_data(
            telegram_id=user_id,
            deaths=ghoul.deaths + 1,
            is_dead=True,
            death_cause=cause.value
        )

    async def reset_for_rebirth(self, user_id: int, kagune_type: str) -> None:
        await self.ghoul_repo.change_data(
            telegram_id=user_id,
            snap_count=0,
            coffee_count=0,
            kagune_type=kagune_type,
            kagune_strength=1,
            kagune_was_obtained=True,
            strength=1,
            dexterity=1,
            speed=1,
            hp=5,
            regen=5,
            eat_humans=0,
            eat_ghouls=0,
            hunger=100,
            hunger_updated_at=datetime.now(timezone.utc),
            is_dead=False,
            death_cause=None,
            is_kakuja=False,
        )

    @staticmethod
    def get_price_kagune(level: int) -> int:
        """Расчёт стоимости улучшения кагуне."""

        base = game_cfg.kagune.start_price
        multiplier = game_cfg.kagune.price_multiplier

        safe_level = min(level, 1000)
        return int(base * (multiplier ** (safe_level - 1)))

    @staticmethod
    def get_kagune_collection(kagune_type: str | None) -> MediaCollection:
        """Папка с гифками для типа кагуне (без учёта регистра)."""

        key = (kagune_type or "").strip().lower()
        return KAGUNE_COLLECTIONS.get(key, MediaCollection.KAGUNE_BIKAKU)

    @staticmethod
    def calculate_power(ghoul: GhoulData) -> int:
        """Подсчёт боевой мощи.
          Складывает текущие статы из бд и уровень кагуне
        """

        base_power = sum(getattr(ghoul, field, 0) for field in POWER_FIELDS)
        k = ghoul.kagune_strength
        power = base_power * 4 + int(k * (8 + k * 0.08))

        # Определяем тип кагуне.
        kagune_type = (ghoul.kagune_type or "").lower().strip()
        multiplier = KAGUNE_MULTIPLIER.get(kagune_type, 1.0)

        # Проверяем форму Какуджа (на будущее)
        if ghoul.is_kakuja:
            multiplier += 0.50

        return int(power * multiplier)

    @staticmethod
    def get_danger_rank(power: int) -> str:
        """Определение ранга угрозы
        на основе вычисленной суммарной мощи гуля
        """
        for limit, rank in DANGER_RANKS:
            if power < limit:
                return rank

        return "SSS+"