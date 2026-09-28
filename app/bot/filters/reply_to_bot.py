from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message

class ReplyToBotFilter(BaseFilter):
    async def __call__(self, message: Message, bot: Bot) -> bool:
        reply = message.reply_to_message
        return bool(reply and reply.from_user and reply.from_user.id == bot.id)