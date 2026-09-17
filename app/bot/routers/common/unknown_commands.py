from aiogram import Router, F
from aiogram.types import Message

from app.bot.keyboards.common.help_keyboard import get_help_menu_unknown_command

router = Router()

@router.message(F.text.startswith("/"))
async def unknown_command(message: Message):
    await message.reply(
        "<tg-emoji emoji-id=\"6030848053177486888\">❓</tg-emoji> "
        "<b>Ты чо, далбаёб?</b>\n\n"
        "<i>Такой команды нет, да даже мой разраб с ай-кью комнатной температуры не додумался бы до такого.</i>\n\n"
        "<tg-emoji emoji-id=\"5258461531464539536\">📌</tg-emoji> "
        "<b>Иди лор сначала почитай.</b>",
        reply_markup=get_help_menu_unknown_command()
    )
