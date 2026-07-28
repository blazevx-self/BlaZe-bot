from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus

class GroupOnlyFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.type in {'group', 'supergroup'}

class GroupCreatorFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        member = await message.bot.get_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id
        )

        return member.status == ChatMemberStatus.CREATOR