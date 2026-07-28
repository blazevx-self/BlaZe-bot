from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.core.templates.common.balance_template import process_balance
from app.core.templates.tops.top_bal_template import build_top_bal_text
from app.types.entities import UserData

from app.services.tops.tops_service import top_service

from app.bot.keyboards.tops.tops_keyboard import (
    get_top_money_kb,
    get_balance_top_money_kb,
    get_back_to_top_kb
)

router = Router()

async def _send_or_edit_top_bal(
        event: Message | CallbackQuery,
        user: UserData,
        reply_markup,
        is_refresh: bool = False
):
    result = await top_service.process_tops(user=user, top_type="money")
    text = build_top_bal_text(result)

    if isinstance(event, Message):
        await event.reply(text=text, reply_markup=reply_markup)
        return

    try:
        await event.message.edit_text(text=text, reply_markup=reply_markup)

        if is_refresh:
            await event.answer("Обновлён топчик", show_alert=False)
        else:
            await event.answer()

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
           if is_refresh:
               await event.answer("Изменений в топе нет", show_alert=False)
           else:
               await event.answer()
        else:
            raise

@router.message(F.text.lower() == 'топ балик')
async def top_money_command(message: Message, user: UserData):
    await _send_or_edit_top_bal(
        event=message,
        user=user,
        reply_markup=get_top_money_kb()
    )

@router.callback_query(F.data == 'update_top_money')
async def refresh_top_we(callback: CallbackQuery, user: UserData):
    await _send_or_edit_top_bal(
        event=callback,
        user=user,
        reply_markup=get_balance_top_money_kb(),
        is_refresh=True
    )

@router.callback_query(F.data == 'update_only_top_money')
async def update_top_only(callback: CallbackQuery, user: UserData):
    await _send_or_edit_top_bal(
        event=callback,
        user=user,
        reply_markup=get_top_money_kb(),
        is_refresh=True
    )

@router.callback_query(F.data == 'money_top')
async def ghoul_top_top(callback: CallbackQuery, user: UserData):
    await _send_or_edit_top_bal(
        event=callback,
        user=user,
        reply_markup=get_balance_top_money_kb()
    )

@router.callback_query(F.data == 'back_to_top')
async def back_to_balance(callback: CallbackQuery, user: UserData):
    await _send_or_edit_top_bal(
        event=callback,
        user=user,
        reply_markup=get_top_money_kb()
    )

@router.callback_query(F.data == 'back_balance')
async def back_to_top(callback: CallbackQuery, user: UserData):
    text = process_balance(user=user, from_top=True)
    await callback.message.edit_text(text=text, reply_markup=get_back_to_top_kb())