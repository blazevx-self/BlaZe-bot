from aiogram import Router, F
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.services.chat_service.chat_service import ChatService

from app.bot.filters.group_only import GroupOnlyFilter, GroupModeratorFilter

router = Router()

@router.message(F.text.lower().startswith("новое прощание"), GroupOnlyFilter(), GroupModeratorFilter())
@inject
async def set_goodbye_message_chat(
    message: Message, chat_service: ChatService = Provide[Container.chat_service]
) -> None:
    goodbye_message = message.text[len('новое прощание'):].strip()

    if not goodbye_message:
        await message.reply(
            "❌ <b>Прощание не указано</b>\n\n"
            "<i>После команды необходимо написать текст прощания.</i>\n\n<b>Пример:</b>\n"
            "<code>новое прощание</code>\n\n"
            "До встречи. Спасибо что был в нашем чате"
        )
        return

    await chat_service.set_goodbye_message(
        telegram_id=message.chat.id,
        goodbye_message=goodbye_message
    )

    await message.reply(
        f"✅ <b>Прощальное сообщение обновлено.</b>\n\n"
        f"<b>Новое прощание:</b>\n\n<i>{goodbye_message}</i>"
    )