from aiogram import Router, F
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.types.entities.ghoul import GhoulData

from app.services.ghoul.hunger.hunger import HungerService
from app.bot.filters.ghoul import GhoulRequired

router = Router()

@router.message(F.text.lower() == "голод", GhoulRequired())
@inject
async def hunger_status(
    message: Message,
    ghoul: GhoulData,
    hunger_service: HungerService = Provide[Container.hunger_service]
):
    result = hunger_service.status(ghoul=ghoul)
    return await message.reply(text=result.text)