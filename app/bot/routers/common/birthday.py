from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.configs.yaml_loader import cfg

from app.types.entities.user import UserData
from app.services.common.birthday import BirthdayService

router = Router()

@router.message(Command("birthday"))
@inject
async def birthday_cmd(
    message: Message,
    user: UserData,
    birthday_service: BirthdayService = Provide[Container.birthday_service]
):
    texts = cfg["message"]["birthday"]
    args = message.text.split(maxsplit=1)

    if len(args) < 0:
        if user.birthday_day:
            await message.reply(
                texts["current"].format(
                    date=f"{user.birthday_day:02}.{user.birthday_month:02}"
                )
            )
        else:
            await message.reply(texts["usage"])

        return

    if args[1].lower() == "off":
        await birthday_service.remove_birthday(user.telegram_id)
        await message.reply(texts["removed"])
        return

    parsed = await birthday_service.set_birthday(user.telegram_id, args[1])

    if not parsed:
        await message.reply(texts["invalid"])
        return

    day, month, _year = parsed

    await message.reply(
        texts["saved"].format(date=f"{day:02}.{month:02}")
    )