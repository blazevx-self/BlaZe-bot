import random
import time

from app.configs.yaml import cfg
from app.configs.game import game_cfg
from app.core.enums import ResultStatus

from app.types.services_result.ghoul import SnapResult
from app.types.entities import UserData

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

        now = int(time.time())
        cooldown_time = game_cfg.snap.cooldown

        # проверка кулдауна щелка
        if user.last_snap:
            remaining = cooldown_time - (now - user.last_snap)

            if remaining > 0:
                return SnapResult(
                    status=ResultStatus.COOLDOWN,
                    remaining=remaining
                )

        money = game_cfg.snap.award

        try:
            processed = await ghouls_repository.process_snap(
                user_id=user.user_id,
                money=money,
                timestamp=now
            )

        except Exception:
            snap_logger.exception(f"[SNAP] Database processed failed | user_id={user.user_id} | reward={money}")
            raise

        if not processed:
            return SnapResult(status=ResultStatus.NOT_FOUND)
        
        user.money += money
        user.snap += 1
        user.last_snap = now

        snap_logger.info(f"[SNAP] Reward issued | user_id={user.user_id} | money={money} | total_snap={user.snap}")
        
        text = cfg['message']['snap']['snap_up'].format(
                money_won=format_num(money),
                total_snap=format_num(user.snap)
            )

        return SnapResult(
            status=ResultStatus.SUCCESS,
            text=text,
            gif=random.choice(cfg['assets']['snap']['gifs'])
        )

snap_service = SnapService()