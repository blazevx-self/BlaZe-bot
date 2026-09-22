import random

from app.configs.yaml_loader import cfg
from app.configs.game import game_cfg

from app.core.enums import ResultStatus
from app.core.enums.cooldown_action import CooldownAction

from app.types.services_result.ghoul import CoffeeResult
from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.services.cooldown import CooldownService

from app.database.repositories.ghoul import GhoulRepository
from app.database.repositories.common.user import UserRepository

from app.utils.format_num import format_num
from app.utils.time import format_duration
from app.utils.logger import coffee_logger

class CoffeeService:
    def __init__(
        self,
        ghoul_repo: GhoulRepository,
        user_repo: UserRepository,
        cooldown_service: CooldownService
    ):
        self.ghoul_repo = ghoul_repo
        self.user_repo = user_repo
        self.cooldown_service = cooldown_service

    async def drink_coffee(self, user: UserData, ghoul: GhoulData) -> CoffeeResult:
        user_id = user.telegram_id
        required_snap = game_cfg.coffee.required_snap
        reward = game_cfg.coffee.award

        # проверяем требования щелчков для кофе
        if ghoul.snap_count < required_snap:
            needed = required_snap - ghoul.snap_count

            return CoffeeResult(
                status=ResultStatus.NOT_ENOUGH_SNAP,
                text=cfg['message']['coffee']['coffee_snap_limit'].format(needed=needed)
            )
        
        # Проверяем кулдаун передозировки
        overdose_remaining = await self.cooldown_service.remaining(
            telegram_id=user_id,
            action=CooldownAction.COFFEE_OVERDOSE
        )

        if overdose_remaining > 0:
            return CoffeeResult(
                status=ResultStatus.OVERDOSE_COOLDOWN,
                text=cfg['message']['coffee']['overdose_2'].format(time=format_duration(overdose_remaining))
            )

        coffee_remaining = await self.cooldown_service.remaining(
            telegram_id=user_id,
            action=CooldownAction.COFFEE
        )

        # Слишком частое употребление
        if coffee_remaining > 0:
            await self.cooldown_service.set(
                telegram_id=user_id,
                action=CooldownAction.COFFEE_OVERDOSE,
                duration=game_cfg.coffee.overdose_cooldown
            )

            return CoffeeResult(
                status=ResultStatus.OVERDOSE,
                text=cfg['message']['coffee']['overdose_1']
            )

        try:
            await self.ghoul_repo.increment_coffee_count(telegram_id=user_id)

            new_money = await self.user_repo.change_money(
                telegram_id=user_id,
                amount=reward
            )

            await self.cooldown_service.set(
                telegram_id=user_id,
                action=CooldownAction.COFFEE,
                duration=game_cfg.coffee.cooldown
            )
        except Exception:
            coffee_logger.exception(f"[COFFEE] Drink coffee failed | user_id={user_id} | reward={reward}")
            raise

        ghoul.coffee_count += 1
        user.money = new_money
        coffee_total = ghoul.coffee_count

        coffee_logger.info(f"[COFFEE] Success drink | user_id={user_id} | reward={reward} | total_coffee={coffee_total}")

        text = cfg['message']['coffee']['coffee_up'].format(
            money=format_num(reward),
            coffee_total=format_num(coffee_total)
        )

        coffee_gif = random.choice(cfg['assets']['coffee']['gifs'])

        return CoffeeResult(
            status=ResultStatus.SUCCESS,
            text=text,
            gif=coffee_gif
        )