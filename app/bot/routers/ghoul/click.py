import time

from aiogram import Router, F
from aiogram.types import Message

from app.configs.yaml import cfg
from app.core.enums import ResultStatus
from app.bot.filters.ghoul_filters import GhoulRequired

from app.services.ghouls.click_service import click_service
from app.types.entities import UserData
from app.utils.time import format_duration

router = Router()

@router.message(F.text.lower() == 'щелк', GhoulRequired())
async def click(message: Message, user: UserData):
    result = await click_service.process_click(user=user)

    if result.status == ResultStatus.COOLDOWN:
        remaining = result.remaining

        text = cfg['message']['click']['click_cooldown'].format(
            time=format_duration(remaining)
        )

        await message.reply(text=text, parse_mode="HTML")
        return

    user.money = result.new_money
    user.clicks = result.new_clicks
    user.last_click = int(time.time())

    await message.reply_animation(
        animation=result.gif,
        caption=result.text,
        parse_mode="HTML"
    )
