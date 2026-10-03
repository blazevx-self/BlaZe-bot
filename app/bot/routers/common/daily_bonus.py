import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.configs.game import game_cfg
from app.configs.yaml_loader import cfg

from app.core.enums import ResultStatus
from app.core.constants.game.daily_bonus import BONUS_LABELS
from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.services.common.daily_bonus import DailyBonusService
from app.bot.filters.owner import OwnerCallbackFilter
from app.bot.keyboards.common.daily_bonus import get_bonus_keyboard

from app.utils.time import format_duration

router = Router()

@router.message(Command("bonus"))
@router.message(F.text.lower() == "бонус")
@inject
async def bonus(
    message: Message,
    user: UserData,
    daily_bonus_service: DailyBonusService = Provide[Container.daily_bonus_service]
):
    texts = cfg['message']['daily_bonus']
    remaining = await daily_bonus_service.remaining(user=user)

    if remaining > 0:
        await message.reply(texts['cooldown'].format(time=format_duration(remaining, show_seconds=False)))
        return

    await message.reply(
        text=texts['choose'],
        reply_markup=get_bonus_keyboard(user_id=user.telegram_id, boxes=game_cfg.daily_bonus.boxes)
    )

@router.callback_query(F.data.startswith("bonus_open_"), OwnerCallbackFilter())
@inject
async def bonus_open(
    callback: CallbackQuery,
    user: UserData,
    ghoul: GhoulData | None = None,
    daily_bonus_service: DailyBonusService = Provide[Container.daily_bonus_service]
):
    texts = cfg['message']['daily_bonus']
    result = await daily_bonus_service.open_box(user=user, ghoul=ghoul)

    if result.status == ResultStatus.COOLDOWN:
        time = format_duration(result.remaining, show_seconds=False)
        await callback.answer(texts['cooldown_callback'].format(time=time), show_alert=True)
        return

    others = "\n".join(f"• {BONUS_LABELS[reward]}" for reward in result.others)
    text = f"{texts['title']}\n\n{result.text}\n\n{texts['others']}\n{others}"

    try:
        await callback.message.edit_text(text=text, reply_markup=None)
    except TelegramAPIError:
        pass # награда уже выдана - покажем её хотя бы в алерте

    await callback.answer(re.sub(r"<[^>]+>", "", result.text), show_alert=True)