from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.templates.tops.top_kagune_template import build_top_kagune_text

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.services.tops.tops_service import TopsService

from app.bot.filters.ghoul_filters import GhoulRequired
from app.bot.keyboards.tops.tops_keyboard import get_update_top_kagune_kb

router = Router()

@router.message(F.text.lower() == "топ кагуне", GhoulRequired())
@inject
async def top_kagune_cmd(
    message: Message,
    user: UserData,
    ghoul: GhoulData,
    top_service: TopsService = Provide[Container.tops_service]
):
    result = await top_service.tops(user=user, ghoul=ghoul, top_type="kagune")
    text = build_top_kagune_text(result)

    await message.reply(text=text, reply_markup=get_update_top_kagune_kb())

@router.callback_query(F.data == "update_top_kagune")
@inject
async def refresh_top_kagune(
    callback: CallbackQuery,
    user: UserData,
    ghoul: GhoulData,
    top_service: TopsService = Provide[Container.tops_service]
):
    result = await top_service.tops(user=user, ghoul=ghoul, top_type="kagune")
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