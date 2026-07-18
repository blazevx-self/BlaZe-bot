from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.core.templates.tops.top_click_template import build_top_clicks_text

from app.services.tops.tops_service import top_service
from app.bot.keyboards.tops.tops_keyboard import get_update_top_clicks_kb
from app.types.entities import UserData

router = Router()

@router.message(F.text.lower() == "топ щелк")
async def clicks_top_command(message: Message, user: UserData):
    result = await top_service.process_tops(
        user=user,
        top_type="clicks"
    )
    text = build_top_clicks_text(result)

    await message.reply(
        text=text,
        parse_mode='HTML',
        reply_markup=get_update_top_clicks_kb()
    )

@router.callback_query(F.data == "update_top_click")
async def refresh_clicks_top(callback: CallbackQuery, user: UserData):
    result = await top_service.process_tops(
        user=user,
        top_type="clicks"
    )
    text = build_top_clicks_text(result)

    try:
        await callback.message.edit_text(
            text=text,
            parse_mode='HTML',
            reply_markup=get_update_top_clicks_kb()
        )
        await callback.answer("Обновлён топчик", show_alert=False)

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer("Изменений в топе нет", show_alert=False)
        else:
            raise
