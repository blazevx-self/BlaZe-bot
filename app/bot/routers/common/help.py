from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions

from app.config import cfg
from app.core.templates.common.help_template import build_help_text

from app.bot.keyboards.common.start_keyboard import start_keyboard
from app.bot.keyboards.common.help_keyboard import get_help_menu, get_help_menu_back

from app.utils.logger import bot_logger

BACK_HELP_TEXT = cfg['message']['help']['back_help']

router = Router()

@router.message(Command('help'), F.chat.type == 'private')
async def help_me(message: Message) -> None:
    bot_logger.info(
        f"[COMMAND] name=\"{message.from_user.first_name}\" | user_id={message.from_user.id} | "
        f"chat={message.chat.type} | command=\"/help\""
    )
    await message.reply(
        text=build_help_text(),
        parse_mode="HTML",
        reply_markup=get_help_menu(),
        link_preview_options=LinkPreviewOptions(is_disabled=False),
    )

@router.callback_query(F.data == 'help')
async def help_cb(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        text=build_help_text(),
        parse_mode="HTML",
        reply_markup=get_help_menu_back(),
        link_preview_options=LinkPreviewOptions(is_disabled=False),
    )
    await callback.answer()

@router.callback_query(F.data == 'back')
async def back_me(callback: CallbackQuery):
    text = '<tg-emoji emoji-id="5289581576001167896">🤨</tg-emoji> ' + BACK_HELP_TEXT

    await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=start_keyboard())
    await callback.answer()


