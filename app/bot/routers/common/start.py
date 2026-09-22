from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.types.entities.user import UserData

from app.services.common.start import StartService
from app.bot.keyboards.common.start import start_keyboard

router = Router()

@router.message(CommandStart())
@inject
async def cmd_start(
    message: Message,
    bot: Bot,
    user: UserData,
    start_service: StartService = Provide[Container.start_service]
):
    result = await start_service.start(user=user, bot=bot)
    await message.reply(text=result.text, reply_markup=start_keyboard())