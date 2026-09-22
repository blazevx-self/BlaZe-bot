from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions

from app.configs.yaml_loader import cfg
from app.core.templates.common.help import build_help_text

from app.bot.keyboards.common.start import start_keyboard
from app.bot.keyboards.common.help import get_help_menu, get_help_menu_back

router = Router()

@router.message(Command('help'))
async def help_me(message: Message) -> None:
    await message.reply(
        text=build_help_text(),
        reply_markup=get_help_menu(),
        link_preview_options=LinkPreviewOptions(is_disabled=False),
    )

@router.callback_query(F.data == 'help')
async def help_cb(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        text=build_help_text(),
        reply_markup=get_help_menu_back(),
        link_preview_options=LinkPreviewOptions(is_disabled=False),
    )
    await callback.answer()

@router.callback_query(F.data == 'back')
async def back_me(callback: CallbackQuery):
    text = '<tg-emoji emoji-id="5290027337771919383">😒</tg-emoji> ' + cfg['message']['help']['back_help']
    await callback.message.edit_text(text=text, reply_markup=start_keyboard())
    await callback.answer()