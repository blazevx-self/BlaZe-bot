from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from typing import Any, Callable, Dict, Awaitable

class RpPrivateMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.chat.type == "private":
            await event.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Role-Play команды работают только в групповых чатах.</b>\n\n"
                "<i>В личных сообщениях устанавливать и использовать RP-команды нельзя.</i>"
            )
            return None

        return await handler(event, data)