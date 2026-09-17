from aiogram import Router, F
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.services.chat_service.chat_service import ChatService

from app.bot.filters.group_only import GroupOnlyFilter, GroupModeratorFilter

router = Router()

@router.message(F.text.lower() == 'правила', GroupOnlyFilter())
@inject
async def check_chat_rules(
    message: Message, chat_service: ChatService = Provide[Container.chat_service]
) -> None:
    rules = await chat_service.get_rules(telegram_id=message.chat.id)

    if not rules:
        await message.reply(
            "<tg-emoji emoji-id=\"5258389041006518073\">📂</tg-emoji> "
            "<b>В этом чате нет правил.</b>\n\n<i>Чтобы указать новые правила, используйте команду</i> -> <b>новые правила</b>"
        )
        return

    await message.reply(rules)

@router.message(F.text.lower().startswith("новые правила"), GroupOnlyFilter(), GroupModeratorFilter())
@inject
async def set_rules(
    message: Message, chat_service: ChatService = Provide[Container.chat_service]
) -> None:
    rules = message.text[len("новые правила"):].strip()

    if not rules:
        await message.reply(
            "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> "
            "<b>Правила не указаны.</b>\n\n"
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            "<i>После команды необходимо написать текст правил.</i>\n\n<b>Пример:</b>\n"
            "<code>новые правила</code>\n\n"
            "1. Не спамить.\n"
            "2. Не оскорблять участников.\n"
            "3. Соблюдать уважение друг к другу\n"
        )
        return

    await chat_service.set_rules(telegram_id=message.chat.id, rules=rules)
    await message.reply(
        "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
        "Правила чата сохранены."
    )

@router.message(F.text.lower().startswith("удалить правила"), GroupOnlyFilter(), GroupModeratorFilter())
@inject
async def delete_rules(
    message: Message, chat_service: ChatService = Provide[Container.chat_service]
) -> None:
    await chat_service.delete_rules(telegram_id=message.chat.id)
    await message.reply(
        "<tg-emoji emoji-id=\"5258130763148172425\">🗑</tg-emoji> "
        "Все правила чата были удалены."
    )