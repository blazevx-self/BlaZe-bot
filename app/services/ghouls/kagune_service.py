import time
import random

from app.configs.yaml import cfg
from app.core.enums import KaguneStatus, ResultStatus
from app.core.result import result

from app.database.repositories.ghouls_repository import ghouls_repository
from app.services.ghoul_service import ghoul_service

from app.utils.format_num import format_num
from app.utils.user import update_user

# noinspection PyUnusedLocal
# noinspection PyMethodMayBeStatic
class KaguneService:
    """Сервис игровой механики развитие кагуне"""

    async def process_kagune_open(self, user: dict):
        """Выдаёт пользователю первое кагуне случайного типа."""

        user_id = user['user_id']

        chances = cfg['economy']['kagune']['types_chance']
        kagune_type = random.choices(
            list(chances.keys()),
            weights=list(chances.values()),
            k=1
        )[0]

        await ghouls_repository.init_kagune(user_id=user_id, k_type=kagune_type)
        return result(
            ResultStatus.SUCCESS,
            kagune_type=kagune_type
        )

    async def process_kagune(self, user: dict):
        """Обрабатывает улучшения кагуне.

        Проверяет кулдаун, баланс пользователя, повышает уровень кагуне
        и возвращает результат выполнения
        """

        user_id = user['user_id']

        if not user.get('kagune_was_obtained'):
            return result(
                ResultStatus.ERROR,
                kagune_status=KaguneStatus.NOT_OPENED
            )

        now = int(time.time())
        cooldown = cfg['economy']['kagune']['cooldown']

        # ограничение скорости прокачки (ап раз в 15 минут)
        if now - user.get('kagune_last_grow', 0) < cooldown:
            remaining = cooldown - (now - user['kagune_last_grow'])
            return result(
                ResultStatus.COOLDOWN,
                kagune_status=KaguneStatus.COOLDOWN,
                remaining=remaining
            )

        current_money = user['money']
        level = int(user['kagune_lvl'])
        price = ghoul_service.get_price(level)

        # проверка баланса перед апом
        if current_money < price:
            return result(
                ResultStatus.INSUFFICIENT_FUNDS,
                kagune_status=KaguneStatus.NOT_ENOUGH_MONEY,
                notification=cfg['message']['error_kagune']['not_enough_money'].format(
                    money=format_num(price - current_money)
                )
            )

        new_level = level + 1

        await ghouls_repository.update_kagune_level(
            user_id=user_id,
            new_lvl=new_level,
            price=price,
            timestamp=now,
        )

        text = cfg['message']['kagune']['kagune_up'].format(
            new_lvl=new_level,
            price=format_num(price)
        )

        user = update_user(
            user,
            money=current_money - price,
            kagune_lvl=new_level,
            kagune_last_grow=now
        )

        return result(
            ResultStatus.SUCCESS,
            text=text,
            gif=ghoul_service.get_kagune_gif(new_level)
        )

kagune_service = KaguneService()
