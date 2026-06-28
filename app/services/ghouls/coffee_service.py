import time
import random

from app.configs.yaml import cfg
from app.core.enums.coffee_status import CoffeeStatus

from app.database.repositories.ghouls_repository import ghouls_repository

from app.utils.format_num import format_num
from app.utils.user import update_user

# noinspection PyUnusedLocal
# noinspection PyMethodMayBeStatic
class CoffeeService:
    async def process_coffee(self, user: dict) -> dict:
        user_id = user['user_id']

        now = int(time.time())
        required_clicks = cfg['economy']['coffee']['required_clicks']

        # проверка требования кликов для кофе
        if user.get('clicks', 0) < required_clicks:
            needed = required_clicks - user['clicks']

            return {
                "status": CoffeeStatus.NOT_ENOUGH_CLICKS,
                "text": cfg['message']['coffee']['not_coffee'].format(needed=needed),
                "animation": None
            }

        cooldown = user.get('coffee_cooldown')
        is_cooldown = cooldown and now < cooldown

        if is_cooldown:
            remaining = cooldown - now
            hours = remaining // 3600
            minutes = (remaining % 3600 // 60)

            return {
                "status": CoffeeStatus.OVERDOSE_COOLDOWN,
                "text": cfg['message']['coffee']['overdose_2'].format(hours=hours, minutes=minutes),
                "animation": None,
            }

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

            user['coffee_cooldown'] = cooldown_time

            return {
                "status": CoffeeStatus.OVERDOSE,
                "text": cfg['message']['coffee']['overdose_1'],
                "animation": None
            }

        reward_min, reward_max = cfg['economy']['coffee']['reward']
        money = random.randint(reward_min, reward_max)

        await ghouls_repository.drink_coffee_success(
            user_id=user_id,
            amount=money,
            current_time=now
        )

        user = update_user(
            user,
            money=user.get('money', 0) + money,
            coffee_total=user.get('coffee_total', 0) + 1,
            coffee_last_time=now,
            coffee_cooldown=0
        )

        text = cfg['message']['coffee']['coffee_up'].format(
            money=format_num(money),
            coffee_total=format_num(user['coffee_total'])
        )

        coffee_gif = random.choice(cfg['message']['coffee']['gifs'])

        return {
            "status": CoffeeStatus.SUCCESS,
            "text": text,
            "animation": coffee_gif
        }

coffee_service = CoffeeService()

