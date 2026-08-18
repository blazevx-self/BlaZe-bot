from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app.types.entities import UserData

from app.services.common.start_service import start_service
from app.bot.keyboards.common.start_keyboard import start_keyboard

from app.utils.logger import bot_logger

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, user: UserData):
    result = await start_service.process_start(user=user, bot=bot)
    await message.reply(text=result.text, reply_markup=start_keyboard())