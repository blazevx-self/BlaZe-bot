import time
import random

from app.configs.yaml import cfg
from app.core.enums import ResultStatus
from app.types.services_types.ghoul import CoffeeResult
from app.database.repositories.ghouls_repository import ghouls_repository

from app.utils.format_num import format_num

# noinspection PyMethodMayBeStatic
class CoffeeService:
    """Сервис игровой механики употребления кофе."""

    async def process_coffee(self, user: dict) -> CoffeeResult:
        """Обрабатывает употребления кофе.

        Проверяет ограничения, выдаёт награду, обновляет данные игрока
        и возвращает результат
        """

        user_id = user['user_id']
        now = int(time.time())
        required_clicks = cfg['economy']['coffee']['required_clicks']

        # проверка требования кликов для кофе
        if user.get('clicks', 0) < required_clicks:
            needed = required_clicks - user['clicks']
            text = cfg['message']['coffee']['not_coffee'].format(needed=needed)

            return CoffeeResult(
                status=ResultStatus.NOT_ENOUGH_CLICKS,
                text=text,
            )

        cooldown = user.get('coffee_cooldown')
        is_cooldown = cooldown and now < cooldown

        if is_cooldown:
            remaining = cooldown - now
            hours = remaining // 3600
            minutes = (remaining % 3600 // 60)

            return CoffeeResult(
                status=ResultStatus.OVERDOSE_COOLDOWN,
                text=cfg['message']['coffee']['overdose_2'].format(
                    hours=hours,
                    minutes=minutes
                )
            )

        wait_time = cfg['economy']['coffee']['cooldown']
        overdose_time = cfg['economy']['coffee']['overdose_cooldown']
        last_drink = user.get('coffee_last_time', 0)

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

        reward_min, reward_max = cfg['economy']['coffee']['reward']
        money = random.randint(reward_min, reward_max)

        await ghouls_repository.drink_coffee_success(
            user_id=user_id,
            amount=money,
            current_time=now
        )

        new_money = user.get('money', 0) + money
        new_coffe_total = user.get('coffee_total', 0) + 1

        text = cfg['message']['coffee']['coffee_up'].format(
            money=format_num(money),
            coffee_total=format_num(new_coffe_total)
        )

        coffee_gif = random.choice(cfg['message']['coffee']['gifs'])

        return CoffeeResult(
            status=ResultStatus.SUCCESS,
            text=text,
            gif=coffee_gif,
            new_money=new_money,
            new_coffee_total=new_coffe_total,
            new_coffee_cooldown=0
        )

coffee_service = CoffeeService()

