from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.templates.common.balance import process_balance

from app.types.entities.user import UserData

from app.database.repositories.common.user import UserRepository
from app.services.common.family import FamilyService

from app.bot.filters.owner import OwnerCallbackFilter
from app.bot.keyboards.tops.tops import get_balance_in_top_kb

router = Router()

async def wallet(
    user: UserData,
    user_repo: UserRepository,
    family_service: FamilyService
) -> int:
    row = await user_repo.get(user.telegram_id)

    if row is None:
        return user.money

    family_id = await family_service.family_repo.family_id_of(row.id)

    if family_id is None:
        return user.money

    family = await family_service.family_repo.get(family_id)
    return family.money if family else user.money

@router.message(F.text.lower() == "балик")
@inject
async def balance_me(
    message: Message,
    user: UserData,
    user_repo: UserRepository = Provide[Container.user_repo],
    family_service: FamilyService = Provide[Container.family_service],
) -> None:
    money = await wallet(user, user_repo, family_service)
    text = process_balance(user=user, money=money)
    await message.reply(text=text, reply_markup=get_balance_in_top_kb(user.telegram_id))

@router.callback_query(F.data.startswith("back_to_balance_"), OwnerCallbackFilter())
@inject
async def back_balance(
    callback: CallbackQuery,
    user: UserData,
    user_repo: UserRepository = Provide[Container.user_repo],
    family_service: FamilyService = Provide[Container.family_service],
) -> None:
    money = await wallet(user, user_repo, family_service)
    text = process_balance(user=user, money=money)
    await callback.message.edit_text(text=text, reply_markup=get_balance_in_top_kb(user.telegram_id))
    await callback.answer()