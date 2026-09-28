from html import escape

from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.services.chat.common.ai import AIChatService

from app.bot.filters.reply_to_bot import ReplyToBotFilter
from app.utils.truncate_text import truncate_text

router = Router()

MAX_MESSAGE_LENGTH = 4000

@router.message(F.text, ~F.text.startswith("/"), ReplyToBotFilter(), flags={"ai": True})
@inject
async def reply_to_bot(
    message: Message,
    ai_service: AIChatService = Provide[Container.ai_chat_service],
):
    """Реплай на сообщение бота — отвечает нейросеть. Ключа нет, кулдаун, лимит или ошибка API — молчит."""

    if not message.from_user or not ai_service.enabled:
        return

    if not ai_service.try_acquire(message.from_user.id):
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    reply = message.reply_to_message
    answer = await ai_service.ask(
        question=message.text,
        user_name=message.from_user.first_name,
        context=reply.text or reply.caption,
    )

    if answer:
        await message.reply(escape(truncate_text(answer, MAX_MESSAGE_LENGTH)))