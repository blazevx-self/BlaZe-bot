from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from dependency_injector.wiring import Provide, inject

from app.containers import Container
from app.core.exceptions.chat import FamilyError

from app.types.entities.user import UserData

from app.database.repositories.common.user import UserRepository
from app.services.common.family import FamilyService

from app.bot.filters.group_only import GroupOnlyFilter
from app.bot.filters.owner import OwnerCallbackFilter
from app.bot.keyboards.common.family import divorce_kb

from app.utils.format_num import format_num

from .helpers import FAM, _edit, _mention

router = Router()

@router.message(F.text.lower() == "развод", GroupOnlyFilter())
@router.message(F.text.lower() == "развестись", GroupOnlyFilter())
@inject
async def divorce_cmd(
    message: Message,
    user: UserData,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    me = await user_repo.get(user.telegram_id)

    if me is None or await family_service.family_repo.family_id_of(me.id) is None:
        await message.reply(FAM["single"])
        return

    await message.reply(FAM["divorce"]["ask"], reply_markup=divorce_kb(user.telegram_id))

@router.callback_query(F.data.startswith("fam_div_"), OwnerCallbackFilter())
@inject
async def divorce_cb(
    callback: CallbackQuery,
    user: UserData,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    me = await user_repo.get(user.telegram_id)

    if me is None:
        await callback.answer(FAM["toast_stale"], show_alert=False)
        return

    try:
        result = await family_service.divorce(me.id)
    except FamilyError:
        await callback.answer(FAM["divorce"]["stale"], show_alert=False)
        return

    heir = await user_repo.get_by_id(result.heir_id) if result.heir_id else None

    text = FAM["divorce"]["done"].format(
        name=_mention(me),
        heir=_mention(heir) if heir else "—",
        amount=format_num(result.inherited),
    )

    if not isinstance(callback.message, Message):
        await callback.answer(FAM["toast_stale"], show_alert=False)
        return

    await _edit(callback.message, text)
    await callback.answer(show_alert=False)