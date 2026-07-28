import time

from aiogram import Router, F
from aiogram.types import Message

from app.core.enums import ResultStatus
from app.types.entities import UserData

from app.services.ghouls.coffee_service import coffee_service
from app.bot.filters.ghoul_filters import GhoulRequired


router = Router()

@router.message(F.text.lower() == "пить кофе", GhoulRequired())
async def coffee_handler(message: Message, user: UserData):
    result = await coffee_service.process_coffee(user=user)

    if result.status != ResultStatus.SUCCESS:
        await message.reply(text=result.text)
        return

    user.money = result.new_money
    user.coffee_total = result.new_coffee_total
    user.coffee_cooldown = result.new_coffee_cooldown
    user.coffee_last_time = int(time.time())

    await message.reply_animation(animation=result.gif, caption=result.text,)
