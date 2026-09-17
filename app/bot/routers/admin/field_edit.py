from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.user import UserNotFoundError

from app.services.admin.field_edit import FieldEditService
from app.bot.filters.admin_filter import AdminFilter

router = Router()

@router.message(Command('set_field'), AdminFilter())
@inject
async def set_field(
    message: Message,
    field_edit_service: FieldEditService = Provide[Container.field_edit_service]
):
    if not message.text:
        return

    args = message.text.split(maxsplit=3)

    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_bot:
            await message.reply(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Нельзя изменять поля боту."
            )
            return

        if len(args) < 3:
            await message.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Использование при ответе:</b>\n/set_field «поле» «значение»\n\n"
                f"{field_edit_service.fmt_fields_help()}"
            )
            return

        query = str(message.reply_to_message.from_user.id)
        field = args[1].strip()
        value = args[2].strip()

    else:
        if len(args) < 4:
            await message.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Использование:</b>\n/set_field «id или @username» «поле» «значение»\n\n"
                f"{field_edit_service.fmt_fields_help()}"
            )
            return

        query = args[1].strip()
        field = args[2].strip()
        value = args[3].strip()

    try:
        value = int(value)
    except ValueError:
        await message.reply(
            "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
            "Значение должно быть целым числом."
        )
        return

    try:
        result = await field_edit_service.set_field(
            query=query,
            field=field,
            value=value,
            admin_id=message.from_user.id
        )
    except (UserNotFoundError, ValueError) as e:
        await message.reply(text=str(e))
        return

    await message.answer(field_edit_service.fmt_operation_result(result))