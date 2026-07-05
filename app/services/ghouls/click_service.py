import random
import time

from app.configs.yaml import cfg
from app.configs.game import game_cfg

from app.core.enums import ResultStatus
from app.types.services_types.ghoul import ClickResult

from app.database.repositories.users_repository import user_repository
from app.database.repositories.ghouls_repository import ghouls_repository

from app.utils.format_num import format_num

# noinspection PyMethodMayBeStatic
class ClickService:
    """Сервис игровой механики щелчков"""

    async def process_click(self, user: dict) -> ClickResult:
        """Обрабатывает выполнение команды <Щелк>.

        Проверяет кулдаун, начисляет награду, обновляет статистику пользователя
        и возвращает результат.
        """

        user_id = user['user_id']
        now = int(time.time())
        cooldown_time = game_cfg.click.cooldown
        last_click = user.get('last_click', 0)

        # проверка кулдауна щелка
        if last_click:
            remaining = cooldown_time - (now - last_click)

            if remaining > 0:
                return ClickResult(
                    status=ResultStatus.COOLDOWN,
                    remaining=remaining
                )

        reward_min, reward_max = game_cfg.click.reward
        money = random.randint(reward_min, reward_max)

        await user_repository.add_money(user_id, money)
        await ghouls_repository.add_click(user_id)
        await ghouls_repository.update_last_click(user_id, now)

        new_money = user.get('money', 0) + money
        new_clicks = user.get('clicks', 0) + 1

        text = cfg['message']['click']['click_up'].format(
            money_won=format_num(money),
            total_clicks=format_num(new_clicks)
        )
        click_gif = random.choice(cfg['assets']['click']['gifs'])

        return ClickResult(
            status=ResultStatus.SUCCESS,
            text=text,
            gif=click_gif,
            new_money=new_money,
            new_clicks=new_clicks
        )

click_service = ClickService()