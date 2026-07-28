from aiogram import Router, F
from aiogram.types import Message

from app.services.chat_service import chat_service
from app.bot.filters.group_only import GroupOnlyFilter, GroupCreatorFilter


router = Router()

@router.message(F.text.lower() == 'правила', GroupOnlyFilter())
async def check_chat_rules(message: Message):
    rules = await chat_service.get_rules(chat_id=message.chat.id)

    if not rules:
        await message.reply("<i>В этом чате нет правил. Чтобы указать новые правила, используй команду</i> -> <b>новые правила</b>")
        return

    await message.reply(rules)


@router.message(F.text.lower().startswith("новые правила"), GroupOnlyFilter(), GroupCreatorFilter())
async def set_rules(message: Message):
    rules = message.text[len("новые правила"):].strip()

    if not rules:
        await message.reply(
            "<b>Правила не указаны.</b>\n\n"
            "<i>После команды необходимо написать текст правил.</i>\n\n<b>Пример:</b>\n"
            "<code>новые правила</code>\n\n"
            "1. Не спамить.\n"
            "2. Не оскорблять участников.\n"
            "3. Соблюдать уважение друг к другу\n"
        )
        return

    await chat_service.set_rules(chat_id=message.chat.id, rules=rules)

    await message.reply("<b>Правила чата сохранены.</b>")


@router.message(F.text.lower().startswith("удалить правила"), GroupOnlyFilter(), GroupCreatorFilter())
async def delete_rules(message: Message):
    await chat_service.delete_rules(chat_id=message.chat.id)

    await message.reply("<b>Все правила чата были удалены.</b>")