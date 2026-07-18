from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.services.common.start_service import start_service
from app.bot.keyboards.common.start_keyboard import start_keyboard
from app.types.entities import UserData

from app.utils.logger import bot_logger

router = Router()

@router.message(CommandStart(), F.chat.type == 'private')
async def cmd_start(message: Message, bot: Bot, user: UserData):
    bot_logger.info(
        f"[COMMAND] name=\"{message.from_user.first_name}\" | user_id={message.from_user.id} | "
        f"chat={message.chat.type} | command=\"/start\""
    )

    result = await start_service.process_start(user=user, bot=bot)

    if result.new_money:
        user.money = result.new_money

    if result.is_subscribed:
        user.is_subscribed = True

    await message.reply(
        text=result.text,
        parse_mode="HTML",
        reply_markup=start_keyboard()
    )
