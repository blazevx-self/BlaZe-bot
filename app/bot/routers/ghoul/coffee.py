from aiogram import Router, F
from aiogram.types import Message

from app.bot.filters.ghoul_filters import GhoulRequired
from app.services.ghouls.coffee_service import coffee_service

router = Router()

@router.message(F.text.lower() == "пить кофе", GhoulRequired())
async def coffee_handler(message: Message, user: dict):
    result = await coffee_service.process_coffee(user=user)

    if result['animation']:
        await message.reply_animation(animation=result['animation'], caption=result['text'], parse_mode='HTML')
    else:
        await message.reply(text=result['text'], parse_mode='HTML')