from typing import Optional

from app.configs.game import game_cfg
from app.configs.yaml import cfg

from app.core.constants.game.stats import POWER_FIELDS
from app.core.constants.game.kagune import KAGUNE_MULTIPLIER
from app.core.constants.game.ranks import DANGER_RANKS

from app.types.entities import UserData
from app.database.repositories.users_repository import user_repository

class GhoulService:
    """Общий сервис игровых механик гулей."""

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
    def get_kagune_obtained_gif() -> str:
        return cfg["assets"]["kagune"]["obtained_gif"]


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

ghoul_service = GhoulService()
