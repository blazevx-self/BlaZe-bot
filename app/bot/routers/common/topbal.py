from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.core.templates.common.balance_template import process_balance
from app.core.templates.common.top_bal_template import build_top_text

from app.services.common.top_service import top_service
from app.bot.keyboards.common.top_keyboard import (
    get_update_top_only_kb,
    get_top_ghoul_kb,
    get_back_to_top_kb
)

router = Router()

@router.message(F.text.lower() == 'топ балик')
async def top_command(message: Message, user: dict):
    result = await top_service.process_top(user=user)
    text = build_top_text(result)

    await message.reply(
        text=text,
        parse_mode='HTML',
        reply_markup=get_update_top_only_kb()
    )

@router.callback_query(F.data == 'update_top')
async def refresh_top_we(callback: CallbackQuery, user: dict):
    result = await top_service.process_top(user=user)
    text = build_top_text(result)

    try:
        await callback.message.edit_text(
            text=text,
            parse_mode='HTML',
            reply_markup=get_top_ghoul_kb()
        )
        await callback.answer("Обновлён топчик", show_alert=False)

    except TelegramBadRequest:
        await callback.answer("Изменений в топе нет", show_alert=False)

@router.callback_query(F.data == 'update_top_only')
async def update_top_only(callback: CallbackQuery, user: dict):
    result = await top_service.process_top(user=user)
    text = build_top_text(result)

    try:
        await callback.message.edit_text(
            text=text,
            parse_mode='HTML',
            reply_markup=get_update_top_only_kb()
        )
        await callback.answer("Обновлён топчик", show_alert=False)

    except TelegramBadRequest:
        await callback.answer("Изменений в топе нет", show_alert=False)

@router.callback_query(F.data == 'top')
async def ghoul_top_top(callback: CallbackQuery, user: dict):
    result = await top_service.process_top(user=user)
    text = build_top_text(result)

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=get_top_ghoul_kb()
    )
    await callback.answer()

@router.callback_query(F.data == 'back_to_balance')
async def back_to_balance(callback: CallbackQuery, user: dict):
    text = process_balance(user=user, from_top=True)

    await callback.message.edit_text(
        text=text,
        parse_mode='HTML',
        reply_markup=get_back_to_top_kb()
    )
    await callback.answer()

@router.callback_query(F.data == 'back_to_top')
async def back_to_top(callback: CallbackQuery, user: dict):
    result = await top_service.process_top(user=user)
    text = build_top_text(result)

    await callback.message.edit_text(
        text=text,
        parse_mode='HTML',
        reply_markup=get_update_top_only_kb()
    )


