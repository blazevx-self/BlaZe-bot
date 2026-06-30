from typing import Literal, cast

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.core.enums import ResultStatus
from app.bot.filters.ghoul_filters import GhoulRequired

from app.services.ghouls.stats_service import stats_service

router = Router()

@router.message(F.text.lower() == "качаца", F.chat.type == "private", GhoulRequired())
async def stats_menu(message: Message, user: dict):
    result_data = await stats_service.get_stats_menu(user)

    if not result_data["success"] != ResultStatus.SUCCESS:
        await message.reply(
            result_data.get("notification", "Ошибка"),
            parse_mode='HTML'
        )
        return

    await message.reply(
        text=result_data["text"],
        parse_mode='HTML',
        reply_markup=result_data["keyboard"]
    )

@router.callback_query(F.data.startswith("stat:"))
async def stats(callback: CallbackQuery, user: dict):
    _, stat, amount = callback.data.split(":")
    amount = cast(Literal[1, 3, 5], int(amount))

    result_data = await stats_service.process_stats_upgrade(user, stat, amount)

    if not result_data["success"] != ResultStatus.SUCCESS:
        await callback.answer(
            result_data.get("notification", "Ошибка"),
            show_alert=False,
            parse_mode='HTML'
        )
        return

    await callback.message.edit_text(
        text=result_data["text"],
        reply_markup=result_data["keyboard"],
        parse_mode='HTML'
    )
    await callback.answer(
        result_data.get("notification", "Ошибка"),
        show_alert=False
    )

@router.callback_query(F.data == "locked")
async def locked(callback: CallbackQuery):
    await callback.answer("🔒 Этот уровень недоступен", show_alert=False)