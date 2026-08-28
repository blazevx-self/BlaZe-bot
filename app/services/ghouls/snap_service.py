import random

from app.configs.yaml import cfg
from app.configs.game import game_cfg

from app.core.enums import ResultStatus
from app.core.enums.cooldown_action import CooldownAction

from app.types.services_result.ghoul import SnapResult
from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.services.cooldown_service import CooldownService

from app.database.repositories.ghouls_repository import GhoulRepository
from app.database.repositories.users_repository import UserRepository

from app.utils.format_num import format_num
from app.utils.logger import snap_logger

class SnapService:
    def __init__(
        self,
        ghoul_repo: GhoulRepository,
        user_repo: UserRepository,
        cooldown_service: CooldownService,
    ):
        self.ghoul_repo = ghoul_repo
        self.user_repo = user_repo
        self.cooldown_service = cooldown_service

    async def snap_finger(self, user: UserData, ghoul: GhoulData) -> SnapResult:
        user_id = user.telegram_id
        reward = game_cfg.snap.award
        cooldown = game_cfg.snap.cooldown

        remaining = await self.cooldown_service.remaining(
            telegram_id=user_id,
            action=CooldownAction.SNAP
        )

        if remaining > 0:
            return SnapResult(
                status=ResultStatus.COOLDOWN,
                remaining=remaining
            )

        try:
           await self.ghoul_repo.increment_snap_count(telegram_id=user_id)

           new_balance = await self.user_repo.change_money(
               telegram_id=user_id,
               amount=reward
           )

           await self.cooldown_service.set(
               telegram_id=user_id,
               action=CooldownAction.SNAP,
               duration=cooldown
           )
        except Exception:
            snap_logger.exception(f"[SNAP] Snap finger failed | user_id={user_id} | reward={reward}")
            raise

        ghoul.snap_count += 1
        user.money = new_balance

        snap_logger.info(
            f"[SNAP] Reward issued | user_id={user_id} | "
            f"money={reward} | total_snap={ghoul.snap_count}"
        )
        
        text = cfg['message']['snap']['snap_up'].format(
            money_won=format_num(reward),
            total_snap=format_num(ghoul.snap_count)
        )

        return SnapResult(
            status=ResultStatus.SUCCESS,
            text=text,
            gif=random.choice(cfg['assets']['snap']['gifs'])
        )