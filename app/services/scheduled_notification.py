import asyncio

from datetime import datetime, timezone

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from app.configs.yaml_loader import cfg
from app.containers import session_context

from app.core.enums.notification import NotificationType

from app.database.database import session_factory
from app.database.mappers.ghoul import orm_to_ghoul
from app.database.repositories import GhoulRepository
from app.database.repositories.common.scheduled_notification import (
    ScheduledNotificationRepository,
)

from app.services.ghoul.hunger.calculate_hunger import current_hunger
from app.services.ghoul.hunger.hunger import HungerService

from app.utils.logger import hunger_logger

TICK = 30

class ScheduledNotificationService:
    def __init__(
        self,
        ghoul_repo: GhoulRepository,
        notify_repo: ScheduledNotificationRepository,
        hunger_service: HungerService,
    ):
        self.ghoul_repo = ghoul_repo
        self.notify_repo = notify_repo
        self.hunger_service = hunger_service

    async def process_due(self, bot: Bot) -> None:
        due = await self.notify_repo.get_due(datetime.now(timezone.utc))

        if not due:
            return

        for row in due:
            telegram_id = row.telegram_id
            ntype = row.notification_type
            threshold = row.threshold

            if ntype != NotificationType.HUNGER:
                await self.notify_repo.delete(telegram_id, ntype)
                continue

            await self._handle_hunger(bot, telegram_id, threshold)
            await asyncio.sleep(0.05)

    async def _handle_hunger(
            self, bot: Bot, telegram_id: int, threshold: int | None
    ) -> None:
        ghoul_orm = await self.ghoul_repo.get(telegram_id)

        if ghoul_orm is None:
            await self.notify_repo.delete(telegram_id, NotificationType.HUNGER)
            return

        ghoul = orm_to_ghoul(ghoul_orm)
        now = datetime.now(timezone.utc)
        hunger = current_hunger(ghoul.hunger, ghoul.hunger_updated_at, now)

        if threshold is None or hunger > threshold:
            await self.hunger_service.reschedule(ghoul)
            return

        texts = cfg["message"]["hunger"]

        if threshold == 0:
            text = texts["notify_hunger_zero"]
        else:
            text = texts["notify_hunger"][threshold]

        await self._send(bot, telegram_id, text)
        await self.hunger_service.reschedule(ghoul)

    @staticmethod
    async def _send(bot: Bot, telegram_id: int, text: str) -> None:
        try:
            await bot.send_message(telegram_id, text)
        except TelegramForbiddenError:
            hunger_logger.info("[HUNGER] pm blocked | user_id=%s", telegram_id)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            hunger_logger.exception("[HUNGER] pm failed | user_id=%s", telegram_id)

async def scheduled_notification_loop(container) -> None:
    bot = container.bot()

    while True:
        try:
            async with session_factory() as session:
                token = session_context.set(session)

                try:
                    service = container.scheduled_notification_service()
                    await service.process_due(bot)
                    await session.commit()

                except Exception:
                    await session.rollback()
                    raise

                finally:
                    session_context.reset(token)
        except Exception:
            hunger_logger.exception("[NOTIFY] loop failed")

        await asyncio.sleep(TICK)