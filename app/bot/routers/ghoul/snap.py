import time

from aiogram import Router, F
from aiogram.types import Message

from app.configs.yaml import cfg
from app.core.enums import ResultStatus
from app.types.entities import UserData

from app.services.ghouls.snap_service import snap_service
from app.bot.filters.ghoul_filters import GhoulRequired

from app.utils.time import format_duration

router = Router()

@router.message(F.text.lower() == 'щелк', GhoulRequired())
@router.message(F.text.lower() == 'щёлк', GhoulRequired())
async def snap(message: Message, user: UserData):
    result = await snap_service.process_snap(user=user)

    if result.status == ResultStatus.COOLDOWN:
        remaining = result.remaining

        text = cfg['message']['snap']['snap_cooldown'].format(time=format_duration(remaining))
        
        await message.reply(text=text)
        return

    await message.reply_animation(animation=result.gif, caption=result.text)
