from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.transfer import TransferError
from app.core.exceptions.user import UserNotFoundError

from app.types.entities.user import UserData
from app.services.common.transfer import TransferService

from app.bot.filters.owner import OwnerCallbackFilter
from app.bot.keyboards.common.transfer import get_transfer_confirm_kb

from app.utils.format_num import format_num

router = Router()

@router.message(F.text.regexp(r"(?i)^\s*(перевести|кинуть|подать)\b"))
@inject
async def transfer_cmd(
    message: Message,
    user: UserData,
    transfer_service: TransferService = Provide[Container.transfer_service]
):
    args = message.text.split()
    reply = message.reply_to_message

    try:
        if reply and reply.from_user and len(args) >= 2 and args[1].isdigit():
            amount = int(args[1])
            receiver_id = reply.from_user.id

        elif len(args) >= 3 and args[2].isdigit():
            query = args[1]

            receiver = await transfer_service.resolve_user(query)

            receiver_id = receiver.telegram_id
            amount = int(args[2])

        else:
            await message.reply(
                "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
                "<b>Использование:</b>\n"
                "перевести «id или username» «сумма»\n\n"
                "<b>Команду можно использовать и так:</b> кинуть, подать"
            )
            return

        await transfer_service.validate(
            sender_id=user.telegram_id,
            receiver_id=receiver_id,
            amount=amount
        )

    except (TransferError, UserNotFoundError) as e:
        await message.reply(text=str(e))
        return

    await message.reply(
        text=(
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            "<b>Подтверждение перевода</b>\n\n"
            "<tg-emoji emoji-id=\"5260399854500191689\">👤</tg-emoji> "
            f"Получатель: <code>{receiver_id}</code>\n"
            "<tg-emoji emoji-id=\"5864068125112144897\">💸</tg-emoji> "
            f"Сумма: <b>{format_num(amount)}</b>\n\n"
            f"<b>Подтвердить перевод?</b>"
        ),
        reply_markup=get_transfer_confirm_kb(
            sender_id=user.telegram_id,
            receiver_id=receiver_id,
            amount=amount
        )
    )

@router.callback_query(F.data.startswith("transfer_confirm_"), OwnerCallbackFilter())
@inject
async def transfer_confirm(
    callback: CallbackQuery,
    user: UserData,
    transfer_service: TransferService = Provide[Container.transfer_service]
):
    parts = callback.data.split("_")

    receiver_id = int(parts[2])
    amount = int(parts[3])

    try:
        result = await transfer_service.transfer(
            sender_id=user.telegram_id,
            receiver_id=receiver_id,
            amount=amount
        )

    except (TransferError, UserNotFoundError) as e:
        await callback.message.edit_text(
            text=str(e),
            reply_markup=None
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        text=result.text,
        reply_markup=None
    )
    await callback.answer()

@router.callback_query(F.data.startswith("transfer_cancel_"), OwnerCallbackFilter())
async def transfer_cancel(callback: CallbackQuery):
    await callback.message.edit_text(
        text=(
            "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> "
            "<b>Перевод отменён.</b>"
        ),
        reply_markup=None,
    )
    await callback.answer()