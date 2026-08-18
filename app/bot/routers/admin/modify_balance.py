from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.services.admin.modify_balance import balance_service
from app.bot.filters.admin_filter import AdminFilter

router = Router()

@router.message(Command("modify_balance"), AdminFilter())
async def modify_balance_cmd(message: Message):
    if not message.text:
        return
    
    args = message.text.split(maxsplit=2)

    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_bot:
            await message.reply("⚠️ Нельзя изменить баланс боту.")
            return

        query = str(message.reply_to_message.from_user.id)
        raw_amount = args[1] if len(args) > 1 else None
    
    else:
        if len(args) < 3:
            await message.reply("<b>Использование:</b>\n/modify_balance «id или @username» [+ | - число] ")
            return

        query = args[1]
        raw_amount = args[2]
    
    if not raw_amount.startswith(("+", "-")):
        await message.reply("⚠️ Укажите знак перед числом (например: <code>+5000</code> или <code>-1500</code>).")
        return

    try:
        amount = int(raw_amount)
    except ValueError:
        await message.reply("⚠️ Сумма должна быть целым числом.")
        return

    try:
        result = await balance_service.modify_balance(query, amount)
    except ValueError as e:
        await message.reply(str(e))
        return
    
    await message.answer(balance_service.fmt_operation_result(result))