from typing import Optional

from app.configs.yaml import cfg
from app.core.constants.game.stats import STATUS_FIELDS, POWER_FIELDS
from app.core.constants.game.kagune import KAGUNE_MULTIPLIER
from app.core.constants.game.ranks import DANGER_RANKS

from app.database.repositories.users_repository import user_repository

# noinspection PyMethodMayBeStatic
class GhoulService:
    """Сервис игровых механик гулей."""

    async def check_ghoul(
            self,
            user_id: int,
            cached_user: Optional[dict] = None
    ) -> bool:
        """Проверка: получил ли юзер кагуне
           Если данные уже прилетели из мидлвара
           (passed_user_data), юзаем их,
           если нет - делаем один точечный запрос в бд
        """

        user = cached_user

        if user is None:
            user = await user_repository.get_user_by_id(user_id)

        return bool(user and user.get('kagune_was_obtained'))

    @staticmethod
    def get_price(level: int) -> int:
        """Расчёт стоимости улучшения кагуне."""

        base = cfg['economy']['kagune']['start_price']
        multiplier = cfg['economy']['kagune']['price_multiplier']

        return int(base * (multiplier ** (level - 1)))

    @staticmethod
    def get_kagune_gif(level: int) -> str:
        """За достижение определённых уровней кагуне - игрок получает новую анимацию развития кагуне."""

        gifs = cfg['message']['kagune']['gifs']

        current_gif = gifs[1]

        for required_level in sorted(map(int, gifs.keys())):
            if level >= required_level:
                current_gif = gifs[required_level]
            else:
                break

        return current_gif

    @staticmethod
    def calculate_power(user: dict) -> int:
        """Подсчёт боевой мощи.
          Складывает текущие статы из бд и уровень кагуне
        """

        base_power = sum(user.get(field, 0) for field in POWER_FIELDS)
        base_power += user.get("kagune_lvl", 1)

        # Определяем тип кагуне.
        kagune_type = user.get('kagune_type', '').lower().strip()
        multiplier = KAGUNE_MULTIPLIER.get(kagune_type, 1.0)

        # Проверяем форму Какуджа (на будущее)
        if user.get('kakuja_activated'):
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
        # приводим ключи к int потому что YAML может прочитать как строку или инты в зависимости от парсера.
        ghoul_ranks = {int(k): v for k, v in cfg['economy']['ranks']['ghoul_ranks'].items()}
        current_rank = "E"

        for threshold in sorted(ghoul_ranks):
            if level >= threshold:
                current_rank = ghoul_ranks[threshold]
            else:
                break

        return current_rank

    @staticmethod
    def get_status(user: dict) -> str:
        """Вычисление экономико-боевого статуса гуля
           на основе суммарного power_level из конфига
        """
        weights = cfg['economy']['ranks']['weights']
        statuses = cfg['economy']['ranks']['statuses']

        # вычисление общего power level пользователя на основе активности
        power_level = sum(
            (user.get(field, 0) * weights[weight])
            for field, weight in STATUS_FIELDS.items()
        )

        current_status = "Новенький"
        sorted_statuses = {int(k): v for k, v in statuses.items()}

        for threshold in sorted(sorted_statuses):
            if power_level >= threshold:
                current_status = sorted_statuses[threshold]
            else:
                break

        return current_status

ghoul_service = GhoulService()
