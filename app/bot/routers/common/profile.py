from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from dependency_injector.wiring import inject, Provide

from app.containers import Container

from app.types.entities.ghoul import GhoulData
from app.types.entities.user import UserData

from app.services.common.profile_service import ProfileService
from app.services.ghouls.race_profile_service import RaceProfileService

from app.bot.filters.ghoul_filters import GhoulRequired
from app.bot.filters.owner_filter import OwnerCallbackFilter

from app.bot.keyboards.common.profile_keyboard import get_ras_to_profile_kb, get_profile_to_ras_kb

router = Router()

@router.message(F.text.lower() == 'профиль')
@inject
async def profile_me(
        message: Message,
        user: UserData,
        ghoul: GhoulData,
        profile_service: ProfileService = Provide[Container.profile_service]
):
    result = await profile_service.build_profile(user=user, ghoul=ghoul)

    await message.reply(
        text=result.text,
        reply_markup=get_profile_to_ras_kb(user.telegram_id)
    )

@router.callback_query(F.data.startswith('open_ras_profile_'), GhoulRequired(), OwnerCallbackFilter())
@inject
async def open_ras_profile(
    callback: CallbackQuery,
    user: UserData,
    ghoul: GhoulData,
    race_service: RaceProfileService = Provide[Container.race_profile_service]
):
    result = await race_service.build_race_profile(user=user, ghoul=ghoul)

    await callback.message.edit_text(
        text=result.text,
        reply_markup=get_ras_to_profile_kb(user.telegram_id)
    )
    await callback.answer()