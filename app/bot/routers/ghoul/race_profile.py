from aiogram import Router,F
from aiogram.types import Message, CallbackQuery

from app.bot.filters.ghoul_filters import GhoulRequired

from app.services.common.profile_service import profile_service
from app.services.ghouls.race_profile_service import race_service

from app.bot.keyboards.common.profile_keyboard import get_ras_to_profile_kb, get_profile_to_ras_kb

router = Router()

@router.message(F.text.lower() == 'распрофиль', GhoulRequired())
async def ras_profile(message: Message, user: dict):
    result = await race_service.build_race_profile(user=user)

    await message.reply(text=result['text'], parse_mode='HTML', reply_markup=get_ras_to_profile_kb())

@router.callback_query(F.data == 'open_profile')
async def ras_to_profile(callback: CallbackQuery, user: dict):
    result = await profile_service.build_profile(user=user)

    await callback.message.edit_text(text=result['text'], parse_mode='HTML', reply_markup=get_profile_to_ras_kb())
    await callback.answer()