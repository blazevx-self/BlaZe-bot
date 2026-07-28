from aiogram import Router, F
from aiogram.types import Message

from app.services.chat_service import chat_service
from app.bot.filters.group_only import GroupOnlyFilter, GroupCreatorFilter


router = Router()

@router.message(F.text.lower().startswith("новое приветствие"), GroupOnlyFilter(), GroupCreatorFilter())
async def set_welcome_message_chat(message: Message):
    welcome_message = message.text[len('новое приветствие'):].strip()

    if not welcome_message:
        await message.reply(
            "<b>Приветствие не указано</b>\n\n"
            "<i>После команды необходимо написать текст приветствия.</i>\n\n<b>Пример:</b>\n"
            "<code>новое приветствие</code>\n\n"
            "Добро пожаловать в чат. Почитай правила по команде -> правила"
        )
        return

    await chat_service.set_welcome_message(chat_id=message.chat.id, welcome_message=welcome_message)

    await message.reply(
        f"<b>Приветственное сообщение обновлено.</b>\n\n"
        f"<b>Новое приветствие:</b>\n\n<i>{welcome_message}</i>"
    )