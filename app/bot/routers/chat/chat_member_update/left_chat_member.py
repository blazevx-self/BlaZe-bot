from aiogram import Router

from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    IS_MEMBER, IS_NOT_MEMBER,
)

from app.services.chat_service import chat_service

router = Router()

@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def left_chat_member(event: ChatMemberUpdated) -> None:
    goodbye_message = await chat_service.get_goodbye_message(chat_id=event.chat.id)

    if not goodbye_message:
        return

    await event.bot.send_message(chat_id=event.chat.id, text=goodbye_message)