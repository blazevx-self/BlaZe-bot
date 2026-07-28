from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.core.templates.common.balance_template import process_balance
from app.types.entities import UserData

from app.bot.keyboards.tops.tops_keyboard import get_balance_in_top_kb


router = Router()

@router.message(F.text.lower() == 'балик')
async def balance_me(message: Message, user: UserData) -> None:
    text = process_balance(user=user)
    await message.reply(text=text, reply_markup=get_balance_in_top_kb())


@router.callback_query(F.data == "back_to_balance")
async def back_balance(callback: CallbackQuery, user: UserData) -> None:
    text = process_balance(user=user)
    await callback.message.edit_text(text=text, reply_markup=get_balance_in_top_kb())
    await callback.answer()