from aiogram import Router, F
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.configs.yaml_loader import cfg

from app.core.enums import ResultStatus
from app.core.enums.media import MediaCollection

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.services.ghoul.hunger.hunger import HungerService
from app.services.media import MediaService

from app.bot.filters.ghoul import GhoulRequired

from app.utils.time import format_duration
from app.utils.send_media import reply_media

router = Router()

@router.message(F.text.lower() == "сожрать человека", GhoulRequired())
@inject
async def eat_human(
    message: Message,
    ghoul: GhoulData,
    user: UserData,
    hunger_service: HungerService = Provide[Container.hunger_service],
    media_service: MediaService = Provide[Container.media_service]
):
    result = await hunger_service.eat_human(ghoul=ghoul, user=user)

    if result.status == ResultStatus.COOLDOWN:
        text = cfg['message']['hunger']['eat_cooldown'].format(
            time=format_duration(result.remaining, show_seconds=False)
        )

        await message.reply(text=text)
        return

    if result.status == ResultStatus.FULL:
        await message.reply(text=result.text)
        return

    await reply_media(
        message=message,
        media_service=media_service,
        collection=MediaCollection.EAT_HUMAN,
        caption=result.text
    )