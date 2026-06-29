import random

from aiogram import Router, F
from aiogram.types import Message
from app.configs.yaml import cfg

router = Router()

@router.message(F.text.lower() == 'бот')
async def check_bot(message: Message):
    phrases = cfg.get('bot_responses')

    if not phrases or not isinstance(phrases, list):
        phrases = [
        'Я тут, мой маленький гуль',
        'Чо тебе бездарь нищий',
        'шо ты хотел?'
        ]

    response = random.choice(phrases)
    await message.reply(response)