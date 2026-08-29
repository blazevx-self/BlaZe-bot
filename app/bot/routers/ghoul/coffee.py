from aiogram import Router, F
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.enums import ResultStatus

from app.types.entities.ghoul import GhoulData
from app.types.entities.user import UserData

from app.services.ghouls.coffee_service import CoffeeService
from app.bot.filters.ghoul_filters import GhoulRequired

router = Router()

@router.message(F.text.lower() == "пить кофе", GhoulRequired())
@inject
async def coffee_handler(
    message: Message,
    user: UserData,
    ghoul: GhoulData,
    coffee_service: CoffeeService = Provide[Container.coffee_service]
):
    result = await coffee_service.drink_coffee(user=user, ghoul=ghoul)

    if result.status != ResultStatus.SUCCESS:
        await message.reply(text=result.text)
        return

    await message.reply_animation(animation=result.gif, caption=result.text,)