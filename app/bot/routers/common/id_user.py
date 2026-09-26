from html import escape

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.utils.truncate_text import truncate_text

router = Router()

@router.message(Command("id"))
async def id_cmd(message: Message):
    if not message.from_user:
        return

    lines = []
    reply = message.reply_to_message

    if reply and reply.from_user:
        lines.append(
            f"<b>{escape(truncate_text(reply.from_user.full_name))}:</b> "
            f"<code>{reply.from_user.id}</code>"
        )

    lines.append(f"<b>Ваш ID:</b> <code>{message.from_user.id}</code>")

    if message.chat.type in ("group", "supergroup"):
        lines.append(f"<b>ID чата:</b> <code>{message.chat.id}</code>")

    await message.reply(
        "<tg-emoji emoji-id=\"5884366771913233289\">✈️</tg-emoji> "
        "<b>Идентификаторы</b>\n\n" + "\n".join(lines)
    )