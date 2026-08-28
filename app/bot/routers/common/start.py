from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.types.entities.user import UserData

from app.services.common.start_service import StartService
from app.bot.keyboards.common.start_keyboard import start_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, user: UserData, start_service: StartService):
    result = await start_service.start(user=user, bot=bot)
    await message.reply(text=result.text, reply_markup=start_keyboard())