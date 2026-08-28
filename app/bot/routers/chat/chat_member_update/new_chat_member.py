from aiogram import Router

from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    IS_MEMBER, IS_NOT_MEMBER,
)
from aiogram.exceptions import TelegramAPIError

from app.services.chat_service.chat_service import ChatService
from app.database.repositories.chats_repository import ChatRepository

from app.utils.logger import bot_logger, error_logger

router = Router()

@router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def bot_added(event: ChatMemberUpdated, chat_repo: ChatRepository):
    await chat_repo.upsert(
        telegram_id=event.chat.id,
        title=event.chat.title,
        username=event.chat.username
    )

    bot_logger.info(
        f"[BOT] Added | title_chat=\"{event.chat.title}\" | chat_id={event.chat.id} | "
        f"chat_username={event.chat.username} | type={event.chat.type}"
    )

    try:
       await event.bot.send_message(
           chat_id=event.chat.id,
           text="Ебать, вы меня добавили? Ну пиздата конечно! Я тупой даунский бот ✌️"
       )

    except TelegramAPIError as e:
        error_logger.exception(
            f"[BOT] Welcome message failed | chat_id={event.chat.id} | "
            f"chat_username={event.chat.username} | error={e}"
        )

@router.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def bot_removed(event: ChatMemberUpdated):
    bot_logger.info(
        f"[BOT] Removed | title_chat=\"{event.chat.title}\" | "
        f"chat_id={event.chat.id} | chat_username={event.chat.username} | type={event.chat.type}"
    )

@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def member_joined(event: ChatMemberUpdated, chat_service: ChatService):
    welcome_message = await chat_service.get_welcome_message(telegram_id=event.chat.id)

    if not welcome_message:
        return

    await event.bot.send_message(chat_id=event.chat.id, text=welcome_message)