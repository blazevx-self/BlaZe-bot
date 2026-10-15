from datetime import datetime, timezone

from aiogram import Router, F
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.configs.yaml_loader import cfg
from app.containers import Container

from app.core.enums.death_cause import DeathCause

from app.types.entities.ghoul import GhoulData
from app.types.entities.user import UserData

from app.services import GhoulService
from app.services.ghoul.hunger.hunger import HungerService
from app.services.ghoul.hunger.calculate_hunger import current_hunger

from app.bot.filters.ghoul import GhoulRequired

router = Router()

@router.message(F.text.lower() == "голод", GhoulRequired())
@inject
async def hunger_status(
    message: Message,
    ghoul: GhoulData,
    user: UserData,
    hunger_service: HungerService = Provide[Container.hunger_service],
    ghoul_service: GhoulService = Provide[Container.ghoul_service]
):
    hunger = current_hunger(
        ghoul.hunger,
        ghoul.hunger_updated_at,
        datetime.now(timezone.utc),
    )

    if hunger <= 0 and not ghoul.is_dead:
        await ghoul_service.apply_death(user.telegram_id, DeathCause.HUNGER)
        await message.reply(cfg["message"]["death"]["notify"]["hunger"])
        return

    result = hunger_service.status(ghoul=ghoul)
    await message.reply(text=result.text)