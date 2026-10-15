from datetime import datetime, timezone, timedelta

from app.configs.yaml_loader import cfg
from app.configs.game import game_cfg

from app.core.enums import ResultStatus
from app.core.enums.cooldown_action import CooldownAction
from app.core.enums.daily_bonus import EffectKey
from app.core.enums.notification import NotificationType

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData
from app.types.services_result.ghoul import EatHumanResult, HungerResult

from app.services.cooldown import CooldownService
from app.services.ghoul.hunger.calculate_hunger import (
    current_hunger,
    hunger_tier,
    hours_until_starved,
    restore_hunger,
    next_threshold
)

from app.database.repositories.ghoul.ghoul import GhoulRepository
from app.database.repositories.common.scheduled_notification import (
    ScheduledNotificationRepository
)
from app.database.mappers.ghoul import orm_to_ghoul

from app.utils.format_num import format_num
from app.utils.logger import hunger_logger
from app.utils.time import format_duration
from app.utils.effects import apply_effect

class HungerService:
    def __init__(
        self,
        ghoul_repo: GhoulRepository,
        cooldown_service: CooldownService,
        notify_repo: ScheduledNotificationRepository,
    ):
        self.ghoul_repo = ghoul_repo
        self.cooldown_service = cooldown_service
        self.notify_repo = notify_repo

    async def reschedule(self, ghoul: GhoulData) -> None:
        now = datetime.now(timezone.utc)

        hunger = current_hunger(ghoul.hunger, ghoul.hunger_updated_at, now)
        threshold = next_threshold(hunger)

        if threshold is None:
            await self.notify_repo.delete(ghoul.telegram_id, NotificationType.HUNGER)
            return

        hours = (hunger - threshold) / game_cfg.hunger.per_hour
        fire_at = now if hours <= 0 else now + timedelta(hours=hours)

        await self.notify_repo.schedule(
            telegram_id=ghoul.telegram_id,
            notification_type=NotificationType.HUNGER,
            fire_at=fire_at,
            threshold=threshold
        )

    async def schedule_for(self, telegram_id: int) -> None:
        row = await self.ghoul_repo.get(telegram_id)

        if row is None:
            return

        await self.reschedule(orm_to_ghoul(row))

    async def eat_human(self, user: UserData, ghoul: GhoulData) -> EatHumanResult:
        user_id = ghoul.telegram_id
        texts = cfg["message"]["hunger"]

        remaining = await self.cooldown_service.remaining(
            telegram_id=user_id,
            action=CooldownAction.EAT_HUMAN
        )

        if remaining > 0:
            return EatHumanResult(
                status=ResultStatus.COOLDOWN,
                remaining=remaining
            )

        now = datetime.now(timezone.utc)
        hunger = current_hunger(ghoul.hunger, ghoul.hunger_updated_at, now)

        if hunger >= game_cfg.hunger.max_hunger:
            await self.reschedule(ghoul)
            return EatHumanResult(
                status=ResultStatus.FULL,
                text=texts["full"],
            )

        restored = game_cfg.hunger.restore
        new_hunger = restore_hunger(hunger, restored)

        try:
            updated = await self.ghoul_repo.change_data(
                telegram_id=user_id,
                hunger=new_hunger,
                hunger_updated_at=now,
                eat_humans=ghoul.eat_humans + 1
            )

            await self.cooldown_service.set(
                telegram_id=user_id,
                action=CooldownAction.EAT_HUMAN,
                duration=apply_effect(
                    user,
                    EffectKey.EAT_COOLDOWN,
                    game_cfg.hunger.eat_cooldown
                )
            )
        except Exception:
            hunger_logger.exception(f"[HUNGER] Eat human failed | user_id={user_id}")
            raise

        ghoul.hunger = new_hunger
        ghoul.hunger_updated_at = now
        ghoul.eat_humans = updated.eat_humans

        hunger_logger.info(
            f"[HUNGER] Ate human | user_id={user_id} | "
            f"hunger={hunger}->{new_hunger} (+{restored}) | total={ghoul.eat_humans}"
        )

        text = texts['eat_success'].format(
            restored=restored,
            hunger=new_hunger,
            count=format_num(ghoul.eat_humans)
        )

        await self.reschedule(ghoul)

        return EatHumanResult(status=ResultStatus.SUCCESS, text=text)

    @staticmethod
    def status(ghoul: GhoulData) -> HungerResult:
        texts = cfg["message"]["hunger"]

        now = datetime.now(timezone.utc)
        hunger = current_hunger(ghoul.hunger, ghoul.hunger_updated_at, now)
        tier = hunger_tier(hunger)
        hours = hours_until_starved(hunger)

        text = texts['status'].format(
            hunger=hunger,
            tier=texts['tiers'][tier],
            time=format_duration(int(hours * 3600), show_seconds=False)
        )

        return HungerResult(status=ResultStatus.SUCCESS, text=text)