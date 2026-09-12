from aiogram import Router, F
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.configs.yaml_loader import cfg

from app.core.enums import ResultStatus
from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.services.ghouls.snap_service import SnapService
from app.bot.filters.ghoul_filters import GhoulRequired

from app.utils.time import format_duration

router = Router()

@router.message(F.text.lower() == 'щелк', GhoulRequired())
@router.message(F.text.lower() == 'щёлк', GhoulRequired())
@inject
async def snap(
    message: Message,
    user: UserData,
    ghoul: GhoulData,
    snap_service: SnapService = Provide[Container.snap_service]
):
    result = await snap_service.snap_finger(user=user, ghoul=ghoul)

    if result.status == ResultStatus.COOLDOWN:
        remaining = result.remaining

        text = cfg['message']['snap']['snap_cooldown'].format(time=format_duration(remaining))
        
        await message.reply(text=text)
        return

    await message.reply_animation(animation=result.gif, caption=result.text)