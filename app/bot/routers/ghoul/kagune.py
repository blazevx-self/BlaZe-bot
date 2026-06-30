from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaAnimation

from app.configs.yaml import cfg
from app.core.enums import ResultStatus

from app.services.ghouls.kagune_service import kagune_service
from app.bot.keyboards.ghoul.kagune_keyboard import get_grow_kagune_kb, get_open_kagune_kb

from app.utils.format_num import format_num
from app.utils.user import update_user

router = Router()

@router.message(F.text.lower() == "растить кагуне")
async def kagune_menu(message: Message, user: dict):
    result_data = await kagune_service.process_kagune(user=user)

    if result_data["status"] == ResultStatus.ERROR:
        text = cfg['message']['kagune']['kagune_1'].format(name=message.from_user.first_name)
        await message.reply(text=text, parse_mode="HTML", reply_markup=get_open_kagune_kb())
        return

    if result_data["status"] == ResultStatus.COOLDOWN:
        remaining = result_data['remaining']

        text = cfg['message']['kagune']['cooldown'].format(
            minutes=remaining // 60,
            seconds=remaining % 60,
        )

        await message.reply(text=text, parse_mode="HTML")
        return

    if result_data["status"] == ResultStatus.INSUFFICIENT_FUNDS:
        missing = result_data['missing']
        text = cfg['message']['errors_kagune']['not_enough_money'].format(money=format_num(missing))
        await message.reply(text=text, parse_mode="HTML")
        return

    await message.reply_animation(
        animation=result_data['gif'],
        caption=result_data['text'],
        parse_mode="HTML"
    )

# noinspection PyUnusedLocal
@router.callback_query(F.data == "kagune_new")
async def kagune_open(callback: CallbackQuery, user: dict):
    result_data = await kagune_service.process_kagune_open(user=user)

    kagune_type = result_data['kagune_type']

    user = update_user(
        user,
        kagune_was_obtained=1,
        kagune_lvl=1,
        kagune_type=kagune_type
    )

    text = cfg['message']['kagune']['kagune_2'].format(
        chosen_type=kagune_type,
        name=callback.from_user.first_name
    )

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=get_grow_kagune_kb()
    )
    await callback.answer()

@router.callback_query(F.data == "kagune_ras")
async def kagune_grow(callback: CallbackQuery, user: dict):
    result_data = await kagune_service.process_kagune(user=user)

    if result_data["status"] == ResultStatus.COOLDOWN:
        remaining = result_data['remaining']
        text = cfg['message']['errors_kagune']['cooldown'].format(
            minutes=remaining // 60,
            seconds=remaining % 60,
        )

        await callback.answer(text=text, show_alert=True)
        return

    if result_data["status"] == ResultStatus.INSUFFICIENT_FUNDS:
        missing = result_data['missing']
        text = cfg['message']['kagune']['not_enough_money'].format(money=format_num(missing))
        await callback.answer(text=text, show_alert=True)
        return

    await callback.message.edit_media(
        media=InputMediaAnimation(
            media=result_data['gif'],
            caption=result_data['text'],
            parse_mode="HTML"
        ),
        reply_markup=None
    )
    await callback.answer()