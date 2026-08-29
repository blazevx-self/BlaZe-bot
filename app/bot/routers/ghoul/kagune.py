from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaAnimation

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.configs.yaml import cfg

from app.core.enums import ResultStatus
from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.services.ghouls.kagune_service import KaguneService
from app.bot.filters.owner_filter import OwnerCallbackFilter

from app.bot.keyboards.ghoul.kagune_keyboard import get_grow_kagune_kb, get_open_kagune_kb

from app.utils.format_num import format_num
from app.utils.time import format_duration

router = Router()

@router.message(F.text.lower() == "растить кагуне")
@inject
async def kagune_menu(
    message: Message,
    user: UserData,
    ghoul: GhoulData,
    kagune_service: KaguneService = Provide[Container.kagune_service]
):
    result = await kagune_service.upgrade_kagune(user=user, ghoul=ghoul)

    if result.status == ResultStatus.NO_KAGUNE:
        text = cfg['message']['kagune']['kagune_1'].format(name=message.from_user.first_name)

        await message.reply(text=text, reply_markup=get_open_kagune_kb(user.telegram_id))
        return

    if result.status == ResultStatus.COOLDOWN:
        remaining = result.remaining

        text = cfg['message']['kagune']['cooldown'].format(time=format_duration(remaining))

        await message.reply(text=text)
        return

    if result.status == ResultStatus.NOT_ENOUGH_MONEY:
        missing = result.missing
        text = cfg['message']['kagune']['not_enough_money'].format(missing=format_num(missing))

        await message.reply(text=text)
        return

    await message.reply_animation(animation=result.gif, caption=result.text,)

@router.callback_query(F.data.startswith("kagune_new_"), OwnerCallbackFilter())
@inject
async def obtained_kagune(
    callback: CallbackQuery,
    user: UserData,
    ghoul: GhoulData,
    kagune_service: KaguneService = Provide[Container.kagune_service]
):
    result = await kagune_service.obtaining_kagune(user=user, ghoul=ghoul)

    text = cfg['message']['kagune']['kagune_2'].format(
        chosen_type=result.kagune_type,
        name=callback.from_user.first_name
    )

    await callback.message.edit_media(
        media=InputMediaAnimation(
            media=result.gif,
            caption=text,
        ),
        reply_markup=get_grow_kagune_kb(user.telegram_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("kagune_ras_"), OwnerCallbackFilter())
@inject
async def kagune_grow(
    callback: CallbackQuery,
    user: UserData,
    ghoul: GhoulData,
    kagune_service: KaguneService = Provide[Container.kagune_service]
):
    result = await kagune_service.upgrade_kagune(user=user, ghoul=ghoul)

    if result.status == ResultStatus.COOLDOWN:
        remaining = result.remaining

        text = cfg['message']['kagune']['cooldown'].format(time=format_duration(remaining))

        await callback.answer(text=text, show_alert=True)
        return

    if result.status == ResultStatus.NOT_ENOUGH_MONEY:
        missing = result.missing
        text = f"💸 Не хватает на балике: {format_num(missing)} BlaZeCoin"

        await callback.answer(text=text, show_alert=False)
        return

    if result.status == ResultStatus.SUCCESS:
        await callback.message.edit_media(
            media=InputMediaAnimation(
                media=result.gif,
                caption=result.text,
            ),
            reply_markup=None
        )
        await callback.answer()