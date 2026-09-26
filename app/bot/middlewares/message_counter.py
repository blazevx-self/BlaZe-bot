from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Message

from dependency_injector.wiring import Provide

from app.containers import Container
from app.database.repositories.chat.chat_member import ChatMemberRepository

class MessageCounterMiddleware(BaseMiddleware):
    """Считает сообщения участников в группах."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
        chat_member_repo: ChatMemberRepository = Provide[Container.chat_member_repo]
    ) -> Any:
        if (
            event.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)
            and event.from_user
            and not event.from_user.is_bot
            and not event.new_chat_members
            and not event.left_chat_member
        ):
            await chat_member_repo.increment_messages(
                chat_telegram_id=event.chat.id,
                user_telegram_id=event.from_user.id
            )

        return await handler(event, data)