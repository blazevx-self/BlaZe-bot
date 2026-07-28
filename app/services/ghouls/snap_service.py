import random
import time

from app.configs.yaml import cfg
from app.configs.game import game_cfg
from app.core.enums import ResultStatus

from app.types.services_result.ghoul import SnapResult
from app.types.entities import UserData

from app.database.repositories.users_repository import user_repository
from app.database.repositories.ghouls_repository import ghouls_repository

from app.utils.format_num import format_num
from app.utils.logger import snap_logger


class SnapService:
    """Сервис игровой механики щелчков"""

    @staticmethod
    async def process_snap(user: UserData) -> SnapResult:
        """Обрабатывает выполнение команды <Щелк>.

        Проверяет кулдаун, начисляет награду, обновляет статистику пользователя
        и возвращает результат.
        """

        user_id = user.user_id
        now = int(time.time())
        cooldown_time = game_cfg.snap.cooldown
        last_snap = user.last_snap

        # проверка кулдауна щелка
        if last_snap:
            remaining = cooldown_time - (now - last_snap)

            if remaining > 0:
                return SnapResult(
                    status=ResultStatus.COOLDOWN,
                    remaining=remaining
                )

        reward_min, reward_max = game_cfg.snap.reward
        money = random.randint(reward_min, reward_max)

        try:
            await user_repository.add_money(user_id, money)
            await ghouls_repository.add_snap(user_id)
            await ghouls_repository.update_last_snap(user_id, now)

        except Exception:
            snap_logger.exception(f"[SNAP] Reward updated failed | user_id={user_id} | reward={money}")
            raise

        new_money = user.money + money
        new_snap = user.snap + 1

        snap_logger.info(f"[SNAP] Reward issued | user_id={user_id} | money={money} | total_snap={new_snap}")

        text = cfg['message']['snap']['snap_up'].format(
            money_won=format_num(money),
            total_snap=format_num(new_snap)
        )
        click_gif = random.choice(cfg['assets']['snap']['gifs'])

        return SnapResult(
            status=ResultStatus.SUCCESS,
            text=text,
            gif=click_gif,
            new_money=new_money,
            new_snap=new_snap
        )

snap_service = SnapService()