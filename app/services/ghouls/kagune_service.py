import time

from app.configs.game import game_cfg
from app.configs.yaml import cfg

from app.core.enums import ResultStatus
from app.types.services_types.ghoul import KaguneResult

from app.database.repositories.ghouls_repository import ghouls_repository
from app.services.ghoul_service import ghoul_service

from app.utils.format_num import format_num

# noinspection PyMethodMayBeStatic
class KaguneService:
    """Сервис игровой механики развитие кагуне"""

    async def process_kagune_open(self, user: dict) -> KaguneResult:
        """Выдаёт пользователю первое кагуне случайного типа."""

        user_id = user['user_id']
        kagune_type = game_cfg.kagune.random_type()

        await ghouls_repository.init_kagune(user_id=user_id, k_type=kagune_type)

        return KaguneResult(
            status=ResultStatus.SUCCESS,
            kagune_type=kagune_type
        )

    async def process_kagune(self, user: dict) -> KaguneResult:
        """Обрабатывает улучшения кагуне.

        Проверяет кулдаун, баланс пользователя, повышает уровень кагуне
        и возвращает результат выполнения
        """

        user_id = user['user_id']

        if not user.get('kagune_was_obtained'):
            return KaguneResult(status=ResultStatus.ERROR)

        now = int(time.time())
        cooldown = game_cfg.kagune.cooldown

        # ограничение скорости прокачки (ап раз в 15 минут)
        if now - user.get('kagune_last_grow', 0) < cooldown:
            remaining = cooldown - (now - user['kagune_last_grow'])
            return KaguneResult(
                status=ResultStatus.COOLDOWN,
                remaining=remaining
            )

        current_money = user['money']
        level = int(user['kagune_lvl'])
        price = ghoul_service.get_price(level)

        # проверка баланса перед апом
        if current_money < price:
            return KaguneResult(
                status=ResultStatus.NOT_ENOUGH_MONEY,
                missing=price - current_money
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

        return KaguneResult(
            status=ResultStatus.SUCCESS,
            text=text,
            gif=ghoul_service.get_kagune_gif(new_level),
            new_lvl=new_level,
            new_money=current_money - price,
        )

kagune_service = KaguneService()
