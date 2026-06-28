from aiogram import Router, F
from aiogram.types import Message

from app.configs.yaml import cfg
from app.core.enums.click_status import ClickStatus
from app.bot.filters.ghoul_filters import GhoulRequired

from app.services.ghouls.click_service import click_service

router = Router()

@router.message(F.text.lower() == 'щелк', GhoulRequired())
async def click(message: Message, user: dict):
    result = await click_service.process_click(user=user)

    status = result['status']

    if status == ClickStatus.COOLDOWN:
        remaining = result['remaining']

        minutes = int(remaining // 60)
        seconds = int(remaining % 60)

        text = cfg['message']['click']['click_cooldown'].format(minutes=minutes, seconds=seconds)

        await message.reply(text=text, parse_mode="HTML")
        return

    await message.reply_animation(animation=result['gif'], caption=result['text'], parse_mode="HTML")
