import random

from aiogram import Router, F
from aiogram.types import Message

from app.configs.yaml import cfg
from app.utils.logger import bot_logger

router = Router()

@router.message(F.text.lower() == 'бот')
async def check_bot(message: Message):
    phrases = cfg.get('bot_responses')

    if not phrases or not isinstance(phrases, list):
        phrases = ["Ау?", "Звали?", "Слушаю", "Чего тебе?", "Чо доебались?"]
        bot_logger.warning(f"[BOT RESPONSES FALLBACK USED] user_id={message.from_user.id} | chat={message.chat.type}")

    response = random.choice(phrases)
    await message.reply(response)