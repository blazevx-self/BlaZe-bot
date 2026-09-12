from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from dependency_injector.wiring import inject, Provide

from app.configs.settings import settings
from app.containers import Container

from app.core.enums.rp_commands import TypeRpCommand
from app.types.services_result.rp_commands import RpCommandResult

from app.services.common.rp_commands_service import RpCommandService

from app.bot.middlewares.rp_command_middleware import RpPrivateMiddleware
from app.bot.filters.rp_commands import NewRpCommandOnMedia, RpCommandFilter

router = Router()

router.message.middleware(RpPrivateMiddleware())

@router.message(NewRpCommandOnMedia(TypeRpCommand.PHOTO))
@router.message(NewRpCommandOnMedia(TypeRpCommand.ANIMATION))
@inject
async def set_rp_media(
    message: Message,
    command: str,
    action: str,
    type_command: TypeRpCommand,
    rp_command_service: RpCommandService = Provide[Container.rp_command_service]
) -> None:
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.animation:
        file_id = message.animation.file_id
    else:
        return

    await message.forward(settings.ADMIN_IDS)

    rp_command = await rp_command_service.upsert(
        chat_id=message.chat.id,
        command=command,
        action=action,
        type_command=type_command,
        file_id=file_id
    )

    await message.reply(
        f"✅ <b>Установлена Role-Play команда.</b>\n\n"
        f"📍 Команда {rp_command.command} с действием {rp_command.action}"
    )

@router.message(Command("set_rp"))
@inject
async def set_rp_cmd(
    message: Message,
    command: CommandObject,
    rp_command_service: RpCommandService = Provide[Container.rp_command_service]
) -> None:
    if not command.args:
        await message.reply("ℹ️ <b>Используйте:</b> /set_rp «команда» «действие»")
        return

    args = command.args.split(maxsplit=1)

    if len(args) < 2:
        await message.reply(
            "ℹ️ <b>Используйте:</b> /set_rp «команда» «действие»\n\n"
            "<b>Пример:</b>\nобнять обнял(-а) крепко"
        )
        return

    rp_command = await rp_command_service.upsert(
        chat_id=message.chat.id,
        command=args[0],
        action=args[1],
        type_command=TypeRpCommand.TEXT
    )

    if rp_command is None:
        await message.reply(
            "⚠️ <b>Достигнут лимит Role-Play команд.</b>\n\nМаксимум — <b>20 команд</b> на один чат."
        )
        return

    await message.reply(
        f"✅ <b>Установлена Role-Play команда.</b>\n\n"
        f"📍 Команда <b>{rp_command.command}</b> с действием <b>{rp_command.action}</b>"
    )

@router.message(Command("all_rp"))
@inject
async def get_all_rp(
    message: Message,
    rp_command_service: RpCommandService = Provide[Container.rp_command_service]
) -> None:
    commands = await rp_command_service.get_all(message.chat.id)

    if not commands:
        await message.reply(
            "📭 <b>В этом чате пока нет Role-Play команд.</b>\n\n"
            "ℹ️ <b>Добавьте первую:\n</b> /set_rp «команда» «действие»"
        )
        return

    lines = ["📝 <b>Список всех Role-Play команд чата:</b> \n\n"]
    lines.extend(
        f"<b>{index}.</b> {rp.command} — {rp.action}"
        for index, rp in enumerate(commands, start=1)
    )

    await message.reply("\n".join(lines))

@router.message(Command("del_rp"))
@inject
async def delete_rp(
    message: Message,
    command: CommandObject,
    rp_command_service: RpCommandService = Provide[Container.rp_command_service]
) -> None:
    if not command.args:
        await message.reply("ℹ️ <b>Используйте:</b> /del_rp «команда»")
        return

    rp_command = command.args.split(maxsplit=1)[0]

    deleted = await rp_command_service.delete(
        chat_id=message.chat.id,
        command=rp_command
    )

    if not deleted:
        await message.reply(f"❌ Role-Play команда <b>{rp_command}</b> не найдена.")
        return

    await message.reply(f"🗑 Role-Play команда <b>{rp_command}</b> удалена.")

@router.message(RpCommandFilter())
async def role_play(
    message: Message,
    rp_command: RpCommandResult,
) -> None:
    if not message.from_user or not message.text:
        return

    target_name = _get_target_name(message)

    if target_name is None:
        return

    text = (
        f"<b>{message.from_user.first_name}</b> "
        f"{rp_command.action} "
        f"<b>{target_name}</b>"
    )

    await _send_rp(
        message=message,
        rp_command=rp_command,
        text=text
    )

def _get_target_name(message: Message) -> str | None:
    if message.reply_to_message:
        target = message.reply_to_message.from_user

        if not target:
            return None

        return target.first_name

    args = message.text.split()

    if len(args) < 2:
        return None

    target = args[1]

    if not target.startswith("@"):
        return None

    return target

async def _send_rp(
    message: Message,
    rp_command: RpCommandResult,
    text: str,
) -> None:
    match rp_command.type_command:
        case TypeRpCommand.TEXT:
            await message.reply(text)

        case TypeRpCommand.PHOTO:
            if not rp_command.file_id:
                raise RuntimeError(f"⚠️ Role-Play команда <b>{rp_command.command}</b> не содержит file_id.")

            await message.reply_photo(photo=rp_command.file_id, caption=text)

        case TypeRpCommand.ANIMATION:
            if not rp_command.file_id:
                raise RuntimeError(f"⚠️ Role-Play команда <b>{rp_command.command}</b> не содержит file_id.")

            await message.reply_animation(animation=rp_command.file_id, caption=text)

        case _:
            raise RuntimeError(f"⚠️ Неподдерживаемый тип Role-Play команды: <b>{rp_command.type_command}</b>")