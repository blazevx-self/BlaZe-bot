from aiogram import Router

from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from aiogram.exceptions import TelegramAPIError

from app.utils.logger import bot_logger, error_logger

router = Router()

@router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def bot_added(event: ChatMemberUpdated):
    bot_logger.info(f"[BOT ADDED] name=\"{event.chat.title}\" | id={event.chat.id} | type={event.chat.type}")

    try:
       await event.bot.send_message(
           chat_id=event.chat.id,
           text="Ебать, вы меня добавили? Ну пиздата конечно! Я тупой даунский бот ✌️"
       )
    except TelegramAPIError as e:
        error_logger.error(f"[BOT ADDED MESSAGE FAILED] | id={event.chat.id} | error={e}")

@router.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def bot_removed(event: ChatMemberUpdated):
    bot_logger.info(f"[BOT REMOVED] name=\"{event.chat.title}\" | id={event.chat.id} | type={event.chat.type}")


