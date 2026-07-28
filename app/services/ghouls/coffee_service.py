import time
import random

from app.configs.yaml import cfg
from app.configs.game import game_cfg

from app.core.enums import ResultStatus

from app.types.services_result.ghoul import CoffeeResult
from app.types.entities import UserData

from app.database.repositories.ghouls_repository import ghouls_repository

from app.utils.format_num import format_num
from app.utils.time import format_duration
from app.utils.logger import coffee_logger


class CoffeeService:
    """Сервис игровой механики употребления кофе."""

    @staticmethod
    async def process_coffee(user: UserData) -> CoffeeResult:
        """Обрабатывает употребления кофе.

        Проверяет ограничения, выдаёт награду, обновляет данные игрока
        и возвращает результат
        """

        user_id = user.user_id
        now = int(time.time())
        required_snap = game_cfg.coffee.required_snap

        # проверка требования кликов для кофе
        if user.snap < required_snap:
            needed = required_snap - user.snap
            text = cfg['message']['coffee']['coffee_snap_limit'].format(needed=needed)

            return CoffeeResult(
                status=ResultStatus.NOT_ENOUGH_SNAP,
                text=text,
            )

        cooldown = user.coffee_cooldown
        is_cooldown = cooldown and now < cooldown

        if is_cooldown:
            remaining = cooldown - now

            return CoffeeResult(
                status=ResultStatus.OVERDOSE_COOLDOWN,
                text=cfg['message']['coffee']['overdose_2'].format(
                    time=format_duration(remaining)
                )
            )

        wait_time = game_cfg.coffee.cooldown
        overdose_time = game_cfg.coffee.overdose_cooldown
        last_drink = user.coffee_last_time

        # частое употребление кофе (кофе можно пить 1 раз в 30 минут)
        if last_drink != 0 and (now - last_drink) < wait_time:
            cooldown_time = now + overdose_time

            await ghouls_repository.set_coffee_overdose(
                user_id=user_id,
                cooldown_timestamp=cooldown_time
            )

            return CoffeeResult(
                status=ResultStatus.OVERDOSE,
                text=cfg['message']['coffee']['overdose_1'],
                new_coffee_cooldown=cooldown_time
            )

        reward_min, reward_max = game_cfg.coffee.reward
        money = random.randint(reward_min, reward_max)

        try:
            await ghouls_repository.drink_coffee_success(
                user_id=user_id,
                amount=money,
                current_time=now
            )

        except Exception:
            coffee_logger.exception(f"[COFFEE] Reward issuing failed | user_id={user_id} | reward={money}")
            raise

        new_money = user.money + money
        new_coffe_total = user.coffee_total + 1

        coffee_logger.info(f"[COFFEE] Success drink | user_id={user_id} | reward={money} | total={new_coffe_total}")

        text = cfg['message']['coffee']['coffee_up'].format(
            money=format_num(money),
            coffee_total=format_num(new_coffe_total)
        )

        coffee_gif = random.choice(cfg['assets']['coffee']['gifs'])

        return CoffeeResult(
            status=ResultStatus.SUCCESS,
            text=text,
            gif=coffee_gif,
            new_money=new_money,
            new_coffee_total=new_coffe_total,
            new_coffee_cooldown=0
        )

coffee_service = CoffeeService()

