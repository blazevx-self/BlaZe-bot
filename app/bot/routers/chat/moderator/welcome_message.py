from aiogram import Router, F
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.services.chat.chat_service import ChatService

from app.bot.filters.group_only import GroupOnlyFilter, GroupModeratorFilter

router = Router()

@router.message(F.text.lower().startswith("новое приветствие"), GroupOnlyFilter(), GroupModeratorFilter())
@inject
async def set_welcome_message_chat(
    message: Message, chat_service: ChatService = Provide[Container.chat_service]
) -> None:
    welcome_message = message.text[len('новое приветствие'):].strip()

    if not welcome_message:
        await message.reply(
            "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> "
            "<b>Приветствие не указано</b>\n\n"
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            "<i>После команды необходимо написать текст приветствия.</i>\n\n<b>Пример:</b>\n"
            "<code>новое приветствие</code>\n\n"
            "Добро пожаловать в чат. Почитай правила по команде -> правила"
        )
        return

    await chat_service.set_welcome_message(
        telegram_id=message.chat.id,
        welcome_message=welcome_message
    )

    await message.reply(
        "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
        f"<b>Приветственное сообщение обновлено.</b>\n\n"
        f"<b>Новое приветствие:</b>\n\n<i>{welcome_message}</i>"
    )