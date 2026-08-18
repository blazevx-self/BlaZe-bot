from aiogram import Router, F
from aiogram.types import Message

from app.bot.keyboards.common.help_keyboard import get_help_menu_unknown_command
from app.utils.logger import bot_logger

router = Router()

@router.message(F.text.startswith("/"))
async def unknown_command(message: Message):
    await message.reply(
        "<b>⁉️ Ты чо, далбаёб?</b>\n\n"
        "<i>Такой команды нет, да даже мой разраб с ай-кью комнатной температуры не додумался бы до такого.</i>\n\n"
        "<code>Иди лор сначала почитай.</code>",
        reply_markup=get_help_menu_unknown_command()
    )
