from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.core.templates.tops.top_snap_template import build_top_snap_text
from app.types.entities import UserData

from app.services.tops.tops_service import top_service

from app.bot.filters.ghoul_filters import GhoulRequired
from app.bot.keyboards.tops.tops_keyboard import get_update_top_snap_kb

router = Router()

@router.message(F.text.lower() == "топ щелк", GhoulRequired())
async def snap_top_command(message: Message, user: UserData):
    result = await top_service.process_tops(user=user, top_type="snap")
    text = build_top_snap_text(result)

    await message.reply(text=text, reply_markup=get_update_top_snap_kb())


@router.callback_query(F.data == "update_top_snap")
async def refresh_snap_top(callback: CallbackQuery, user: UserData):
    result = await top_service.process_tops(user=user, top_type="snap")
    text = build_top_snap_text(result)

    try:
        await callback.message.edit_text(text=text, reply_markup=get_update_top_snap_kb())
        await callback.answer("Обновлён топчик", show_alert=False)

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer("Изменений в топе нет", show_alert=False)
        else:
            raise
