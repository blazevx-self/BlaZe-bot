from html import escape

from aiogram import Router

from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    IS_MEMBER,
    IS_NOT_MEMBER
)

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.services.chat.chat_service import ChatService

router = Router()

@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
@inject
async def left_chat_member(
    event: ChatMemberUpdated,
    chat_service: ChatService = Provide[Container.chat_service]
) -> None:
    if event.chat.type not in ("group", "supergroup"):
        return

    member = event.old_chat_member.user
    goodbye_message = await chat_service.get_goodbye_message(telegram_id=event.chat.id)

    if not goodbye_message:
        return

    goodbye_message = goodbye_message.replace(
        "{name}",
        escape(member.first_name)
    )

    await event.bot.send_message(chat_id=event.chat.id, text=goodbye_message)