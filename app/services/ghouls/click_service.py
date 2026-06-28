import random
import time

from app.configs.yaml import cfg
from app.core.enums.click_status import ClickStatus

from app.database.repositories.users_repository import user_repository
from app.database.repositories.ghouls_repository import ghouls_repository

from app.utils.format_num import format_num
from app.utils.user import update_user

# noinspection PyUnusedLocal
# noinspection PyMethodMayBeStatic
class ClickService:
    async def process_click(self, user: dict):
        user_id = user['user_id']
        now = int(time.time())
        cooldown_time = cfg['economy']['click']['cooldown']
        last_click = user.get('last_click', 0)

        # проверка кулдауна щелка
        if last_click:
            remaining = cooldown_time - (now - last_click)

            if remaining > 0:
                return {
                    "status": ClickStatus.COOLDOWN,
                    "remaining": remaining
                }

        reward_min, reward_max = cfg['economy']['click']['reward']
        money = random.randint(reward_min, reward_max)

        await user_repository.add_money(user_id, money)
        await ghouls_repository.add_click(user_id)
        await ghouls_repository.update_last_click(user_id, now)

        user = update_user(
            user,
            money=user.get('money', 0) + money,
            clicks=user.get('clicks', 0) + 1,
            last_click=now
        )

        money_won = format_num(money)
        total_clicks = format_num(user['clicks'])

        text = cfg['message']['click']['click_up'].format(money_won=money_won, total_clicks=total_clicks)
        click_gif = random.choice(cfg['message']['click']['gifs'])

        return {
            "status": ClickStatus.SUCCESS,
            "text": text,
            "gif": click_gif
        }

click_service = ClickService()