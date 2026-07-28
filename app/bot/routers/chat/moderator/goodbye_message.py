from aiogram import Router, F
from aiogram.types import Message

from app.services.chat_service import chat_service
from app.bot.filters.group_only import GroupOnlyFilter, GroupCreatorFilter

router = Router()

@router.message(F.text.lower().startswith("новое прощание"), GroupOnlyFilter(), GroupCreatorFilter())
async def set_welcome_message_chat(message: Message):
    goodbye_message = message.text[len('новое прощание'):].strip()

    if not goodbye_message:
        await message.reply(
            "<b>Прощание не указано</b>\n\n"
            "<i>После команды необходимо написать текст прощания.</i>\n\n<b>Пример:</b>\n"
            "<code>новое прощание</code>\n\n"
            "До встречи. Спасибо что был в нашем чате"
        )
        return

    await chat_service.set_goodbye_message(chat_id=message.chat.id, goodbye_message=goodbye_message)

    await message.reply(
        f"<b>Прощальное сообщение обновлено.</b>\n\n"
        f"<b>Новое прощание:</b>\n\n<i>{goodbye_message}</i>"
    )