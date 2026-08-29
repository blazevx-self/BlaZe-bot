from typing import Literal, cast

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.enums import ResultStatus

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.services.ghouls.stats.stats_service import StatsService
from app.bot.filters.ghoul_filters import GhoulRequired

router = Router()

@router.message(F.text.lower() == "качаца", F.chat.type != "private")
async def stats_menu_group_error(message: Message):
    await message.reply("Команда работает только в личных сообщениях с ботом.")

@router.message(F.text.lower() == "качаца", F.chat.type == "private", GhoulRequired())
@inject
async def stats_menu(
    message: Message,
    user: UserData,
    ghoul: GhoulData,
    stats_service: StatsService = Provide[Container.stats_service]
):
    result = await stats_service.get_stats_menu(user=user, ghoul=ghoul)

    if result.status != ResultStatus.SUCCESS:
        await message.reply(result.notification or "Error stats",)
        return

    await message.reply(text=result.text, reply_markup=result.keyboard)

@router.callback_query(F.data.startswith("stat:"))
@inject
async def stats(
    callback: CallbackQuery,
    user: UserData,
    ghoul: GhoulData,
    stats_service: StatsService = Provide[Container.stats_service]
):
    _, stat, amount = callback.data.split(":")
    amount = cast(Literal[1, 3, 5], int(amount))

    result = await stats_service.stats_upgrade(user=user, ghoul=ghoul, stat=stat, amount=amount)

    if result.status != ResultStatus.SUCCESS:
        await callback.answer(result.notification or "Error stats", show_alert=False,)
        return

    await callback.message.edit_text(text=result.text, reply_markup=result.keyboard)
    await callback.answer(result.notification or "Error stats", show_alert=False)

@router.callback_query(F.data == "locked")
async def locked(callback: CallbackQuery):
    await callback.answer("🔒 Этот уровень недоступен", show_alert=False)