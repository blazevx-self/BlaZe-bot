import time

from app.configs.game import game_cfg
from app.configs.yaml import cfg
from app.core.enums import ResultStatus

from app.types.services_result.ghoul import KaguneResult
from app.types.entities import UserData

from app.database.repositories.ghouls_repository import ghouls_repository
from app.services.ghoul_service import ghoul_service

from app.utils.format_num import format_num
from app.utils.logger import kagune_logger

class KaguneService:
    """Сервис игровой механики развитие кагуне"""

    @staticmethod
    async def process_kagune_open(user: UserData) -> KaguneResult:
        """Выдаёт пользователю первое кагуне случайного типа."""

        user_id = user.user_id
        kagune_type = game_cfg.kagune.random_type()

        try:
            await ghouls_repository.init_kagune(user_id=user_id, k_type=kagune_type)

        except Exception:
            kagune_logger.exception(f"[KAGUNE] Open failed | user_id={user_id} | type={kagune_type}")
            raise

        kagune_logger.info(f"[KAGUNE] First kagune obtained | user_id={user_id} | type={kagune_type}")

        return KaguneResult(
            status=ResultStatus.SUCCESS,
            kagune_type=kagune_type
        )


    @staticmethod
    async def process_kagune(user: UserData) -> KaguneResult:
        """Обрабатывает улучшения кагуне.

        Проверяет кулдаун, баланс пользователя, повышает уровень кагуне
        и возвращает результат выполнения
        """

        user_id = user.user_id

        if not user.kagune_was_obtained:
            kagune_logger.debug(f"[KAGUNE] Upgrade denied | user_id={user_id} | reason=no_kagune")
            return KaguneResult(status=ResultStatus.NO_KAGUNE)

        now = int(time.time())
        cooldown = game_cfg.kagune.cooldown

        # ограничение скорости прокачки (ап раз в 15 минут)
        if now - user.kagune_last_grow < cooldown:
            remaining = cooldown - (now - user.kagune_last_grow)

            return KaguneResult(
                status=ResultStatus.COOLDOWN,
                remaining=remaining
            )

        current_money = user.money
        level = int(user.kagune_lvl)
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

        kagune_logger.info(
            f"[KAGUNE] Level upgraded | user_id={user_id} | "
            f"old_level={level} | new_level={new_level} | price={price} | money_left={current_money - price}"
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
