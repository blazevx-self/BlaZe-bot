from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.core.templates.tops.top_kagune_template import build_top_kagune_text
from app.types.entities import UserData

from app.services.tops.tops_service import top_service

from app.bot.filters.ghoul_filters import GhoulRequired
from app.bot.keyboards.tops.tops_keyboard import get_update_top_kagune_kb

router = Router()

@router.message(F.text.lower() == "топ кагуне", GhoulRequired())
async def top_kagune_command(message: Message, user: UserData):
    result = await top_service.process_tops(user=user, top_type="kagune")
    text = build_top_kagune_text(result)

    await message.reply(text=text, reply_markup=get_update_top_kagune_kb())


@router.callback_query(F.data == "update_top_kagune")
async def refresh_top_kagune(callback: CallbackQuery, user: UserData):
    result = await top_service.process_tops(user=user, top_type="kagune")
    text = build_top_kagune_text(result)

    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=get_update_top_kagune_kb()
        )
        await callback.answer("Обновлён топчик", show_alert=False)

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer("Изменений в топе нет", show_alert=False)
        else:
            raise
