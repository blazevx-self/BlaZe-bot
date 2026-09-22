from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.templates.tops.top_coffee import build_top_coffee_text

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.services.tops.tops import TopsService

from app.bot.filters.ghoul import GhoulRequired
from app.bot.keyboards.tops.tops import get_update_top_coffee_kb

router = Router()

@router.message(F.text.lower() == "топ кофе", GhoulRequired())
@inject
async def coffee_top_cmd(
    message: Message,
    user: UserData,
    ghoul: GhoulData,
    top_service: TopsService = Provide[Container.tops_service]
):
    result = await top_service.tops(user=user, ghoul=ghoul, top_type="coffee")
    text = build_top_coffee_text(result)

    await message.reply(text=text, reply_markup=get_update_top_coffee_kb())

@router.callback_query(F.data == "update_top_coffee")
@inject
async def refresh_coffee_top(
    callback: CallbackQuery,
    user: UserData,
    ghoul: GhoulData,
    top_service: TopsService = Provide[Container.tops_service]
):
    result = await top_service.tops(user=user, ghoul=ghoul, top_type="coffee")
    text = build_top_coffee_text(result)

    try:
        await callback.message.edit_text(text=text, reply_markup=get_update_top_coffee_kb())
        await callback.answer("🔄 Обновлён топчик", show_alert=False)

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer("❌ Изменений в топе нет", show_alert=False)
        else:
            raise