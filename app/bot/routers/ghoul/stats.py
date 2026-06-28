from typing import Literal, cast

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.config import cfg
from app.bot.filters.ghoul_filters import GhoulRequired

from app.services.ghouls.stats_service import stats_service

router = Router()

@router.message(F.text.lower() == "качаца", F.chat.type == "private", GhoulRequired())
async def stats_menu(message: Message, user: dict):
    result = await stats_service.get_stats_menu(user)

    if not result["success"]:
        await message.reply(
            result["notification"],
            parse_mode='HTML'
        )
        return

    await message.reply(
        text=result["text"],
        parse_mode='HTML',
        reply_markup=result["keyboard"]
    )

@router.callback_query(F.data.startswith("stat:"))
async def stats(callback: CallbackQuery, user: dict):
    _, stat, amount = callback.data.split(":")
    amount = cast(Literal[1, 3, 5], int(amount))

    result = await stats_service.process_stats_upgrade(user, stat, amount)

    if not result["success"]:
        await callback.answer(
            result["notification"],
            show_alert=result["show_alert"],
            parse_mode='HTML'
        )
        return

    await callback.message.edit_text(
        text=result["text"],
        reply_markup=result["keyboard"],
        parse_mode='HTML'
    )
    await callback.answer(
        result["notification"],
        show_alert=result["show_alert"]
    )

@router.callback_query(F.data == "locked")
async def locked(callback: CallbackQuery):
    await callback.answer(cfg['message']['callbacks']['locked_button'], show_alert=False)