from typing import Optional
from app.database.repositories.users_repository import user_repository

from app.config import cfg

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
    # расчёт стоимости апа кагуне
    def get_price(level: int) -> int:
        base = cfg['economy']['kagune']['start_price']
        multiplier = cfg['economy']['kagune']['price_multiplier']

        return int(base * (multiplier ** (level - 1)))
    @staticmethod
    # За достижение определённых уровней кагуне
    # игрок получает новую анимацию развития кагуне.
    def get_kagune_gif(level: int) -> str:
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
        base_power = (
            user.get('strength', 0)
            + user.get('agility', 0)
            + user.get("speed", 0)
            + user.get("hp", 0)
            + user.get("regen", 0)
            + user.get("kagune_lvl", 1)
        )

        # Определяем тип кагуне.
        kagune_type = user.get('kagune_type', '').lower().strip()
        multiplier = 1.0

        if 'укаку' in kagune_type:
            multiplier = 1.15
        elif 'коукаку' in kagune_type:
            multiplier = 1.20
        elif 'ринкаку' in kagune_type:
            multiplier = 1.25
        elif 'бикаку' in kagune_type:
            multiplier = 1.10

        # Проверяем форму Какуджа (на будущее)
        if user.get('kakuja_activated'):
            multiplier += 0.50

        return int(base_power * multiplier)

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
    def get_danger_rank(power: int) -> str:
        """Определение ранга угрозы
        на основе вычисленной суммарной мощи гуля
        """
        if power < 500:
            return "F"
        elif power < 1000:
            return "D"
        elif power < 1500:
            return "C"
        elif power < 2000:
            return "B"
        elif power < 3500:
            return "A"
        elif power < 5000:
            return "S"
        elif power < 7500:
            return "SS"
        elif power < 10000:
            return "SSS"

        return "SSS+"

    @staticmethod
    def get_status(user: dict) -> str:
        """Вычисление экономико-боевого статуса гуля
           на основе суммарного power_level из конфига
        """
        weights = cfg['economy']['ranks']['weights']
        statuses = cfg['economy']['ranks']['statuses']

        # вычисление общего power level пользователя на основе активности
        power_level = (
            (user.get("money") or 0) * weights['money']
            + (user.get("clicks") or 0) * weights['clicks']
            + (user.get("coffee_total") or 0) * weights['coffee']
            + (user.get("kagune_lvl") or 1) * weights['kagune_lvl']
            + (user.get('strength') or 1) * weights['strength']
            + (user.get('agility') or 1) * weights['agility']
            + (user.get('speed') or 1) * weights['speed']
            + (user.get('hp') or 1) * weights['hp']
            + (user.get('regen') or 1) * weights['regen']
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
