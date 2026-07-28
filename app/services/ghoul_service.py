from typing import Optional

from app.configs.game import game_cfg
from app.configs.yaml import cfg

from app.core.constants.game.stats import STATUS_FIELDS, POWER_FIELDS
from app.core.constants.game.kagune import KAGUNE_MULTIPLIER
from app.core.constants.game.ranks import DANGER_RANKS

from app.types.entities import UserData
from app.database.repositories.users_repository import user_repository

class GhoulService:
    """Сервис игровых механик гулей."""

    @staticmethod
    async def check_ghoul(
            user_id: int,
            cached_user: Optional[UserData] = None
    ) -> bool:
        """Проверка: получил ли юзер кагуне
           Если данные уже прилетели из мидлвара
           (passed_user_data), юзаем их,
           если нет - делаем один точечный запрос в бд
        """

        user = cached_user

        if user is None:
            user = await user_repository.get_user_by_id(user_id)

        return bool(user and user.kagune_was_obtained)

    @staticmethod
    def get_price(level: int) -> int:
        """Расчёт стоимости улучшения кагуне."""

        base = game_cfg.kagune.start_price
        multiplier = game_cfg.kagune.price_multiplier

        return int(base * (multiplier ** (level - 1)))

    @staticmethod
    def get_kagune_gif(level: int) -> str:
        """За достижение определённых уровней кагуне - игрок получает новую анимацию развития кагуне."""

        gifs = cfg['assets']['kagune']['gifs']

        current_gif = gifs[1]

        for required_level in sorted(map(int, gifs.keys())):
            if level >= required_level:
                current_gif = gifs[required_level]
            else:
                break

        return current_gif

    @staticmethod
    def calculate_power(user: UserData) -> int:
        """Подсчёт боевой мощи.
          Складывает текущие статы из бд и уровень кагуне
        """

        base_power = sum(getattr(user, field, 0) for field in POWER_FIELDS)
        base_power += user.kagune_lvl

        # Определяем тип кагуне.
        kagune_type = (user.kagune_type or "").lower().strip()
        multiplier = KAGUNE_MULTIPLIER.get(kagune_type, 1.0)

        # Проверяем форму Какуджа (на будущее)
        if user.kakuja_activated:
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

    @staticmethod
    def get_rank(level: int) -> str:
        ghoul_ranks = game_cfg.ranks.ghoul_ranks
        current_rank = "E"

        for threshold in sorted(ghoul_ranks):
            if level >= threshold:
                current_rank = ghoul_ranks[threshold]
            else:
                break

        return current_rank

    @staticmethod
    def get_status(user: UserData) -> str:
        """Вычисление экономико-боевого статуса гуля
           на основе суммарного power_level из конфига
        """
        weights = game_cfg.ranks.weights
        statuses = game_cfg.ranks.statuses

        # вычисление общего power level пользователя на основе активности
        power_level = sum(
            (getattr(user, field, 0) * getattr(weights, weight))
            for field, weight in STATUS_FIELDS.items()
        )

        current_status = "Новенький"

        for threshold in sorted(statuses):
            if power_level >= threshold:
                current_status = statuses[threshold]
            else:
                break

        return current_status

ghoul_service = GhoulService()
