from aiogram import Router, F
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.chat import ChatError
from app.services.chat.chat import ChatService
from app.bot.filters.group_only import GroupOnlyFilter, GroupModeratorFilter

router = Router()

@router.message(F.text.lower().startswith("капча вкл"), GroupOnlyFilter(), GroupModeratorFilter())
@inject
async def captcha_on(
    message: Message,
    chat_service: ChatService = Provide[Container.chat_service],
) -> None:
    try:
        await chat_service.set_captcha_enabled(message.chat.id, True)
        await message.reply(
            "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
            "<b>Капча включена.</b>\n\n"
            "<i>Новые участники — должны нажать кнопку, иначе кик.</i>"
        )
    except ChatError as e:
        await message.reply(str(e))
        return

@router.message(F.text.lower().startswith("капча выкл"), GroupOnlyFilter(), GroupModeratorFilter())
@inject
async def captcha_off(
    message: Message,
    chat_service: ChatService = Provide[Container.chat_service],
) -> None:
    try:
        await chat_service.set_captcha_enabled(message.chat.id, False)
        await message.reply(
            "<tg-emoji emoji-id=\"5258130763148172425\">🗑</tg-emoji> "
            "<b>Капча выключена.</b>"
        )
    except ChatError as e:
        await message.reply(str(e))
        return