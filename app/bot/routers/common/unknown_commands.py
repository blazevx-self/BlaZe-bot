from aiogram import Router, F
from aiogram.types import Message

from app.bot.keyboards.common.help_keyboard import get_help_menu_unknown_command
from app.utils.logger import bot_logger

router = Router()

@router.message(F.text.startswith("/"))
async def unknown_command(message: Message):
    command = message.text

    if len(command) > 50:
        command = command[:50] + "..."

    if message.chat.type != "private":
        return

    bot_logger.warning(f"[UNKNOWN COMMAND] user_id={message.from_user.id} | chat={message.chat.type} | command={command}")

    await message.reply(
        "<b>⁉️ Ты чо, далбаёб?</b>\n\n"
        "<i>Такой команды нет, да даже мой разраб с ай-кью комнатной температуры не додумался бы до такого.</i>\n\n"
        "<code>Иди лор сначала почитай.</code>",
        parse_mode="HTML",
        reply_markup=get_help_menu_unknown_command()
    )
