from html import escape

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.filters.group_only import GroupModeratorFilter
from app.utils.truncate_text import truncate_text

router = Router()

@router.message(Command("id"), GroupModeratorFilter())
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

    await message.reply(
        "<tg-emoji emoji-id=\"5884366771913233289\">✈️</tg-emoji> "
        "<b>Идентификатор</b>\n\n" + "\n".join(lines)
    )