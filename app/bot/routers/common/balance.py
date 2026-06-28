from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.core.templates.common.balance_template import process_balance
from app.bot.keyboards.common.top_keyboard import get_ghoul_top_kb

router = Router()

@router.message(F.text.lower() == 'балик')
async def balance_me(message: Message, user: dict) -> None:
    text = process_balance(user=user)

    await message.reply(text=text, parse_mode='HTML', reply_markup=get_ghoul_top_kb())

@router.callback_query(F.data == "back_ghoul")
async def back_ghoul(callback: CallbackQuery, user: dict) -> None:
    text = process_balance(user=user)

    await callback.message.edit_text(text=text, parse_mode='HTML', reply_markup=get_ghoul_top_kb())
    await callback.answer()