from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message

from dependency_injector.wiring import Provide

from app.containers import Container
from app.core.enums.rp_commands import TypeRpCommand

from app.services import RpCommandService

class RpCommandFilter(BaseFilter):
    async def __call__(
        self,
        message: Message,
        rp_command_service: RpCommandService = Provide[Container.rp_command_service],
    ) -> bool | dict[str, Any]:
        if not message.text:
            return False

        command = message.text.split()[0].lower()

        rp_command = await rp_command_service.get(
            chat_id=message.chat.id,
            command=command
        )

        if rp_command is None:
            return False

        return {"rp_command": rp_command}

class NewRpCommandOnMedia(BaseFilter):
    def __init__(self, type_command: TypeRpCommand) -> None:
        self.type_command = type_command

    async def __call__(self, message: Message) -> bool | dict[str, Any]:
        if self.type_command == TypeRpCommand.PHOTO:
            if not message.photo:
                return False

        elif self.type_command == TypeRpCommand.ANIMATION:
            if not message.animation:
                return False

        if not message.caption:
            return False

        args = message.caption.split(maxsplit=2)

        if len(args) < 3 or args[0].lower() != "/set_rp":
            await message.reply("ℹ️ <b>Используйте:</b> /set_rp «команда» «действие»")
            return False

        return {
            "command": args[1].lower(),
            "action": args[2],
            "type_command": self.type_command
        }