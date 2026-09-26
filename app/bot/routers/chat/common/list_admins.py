from aiogram import Router
from aiogram.filters import Command
from aiogram.types import LinkPreviewOptions, Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.services.chat.common.list_admins import ListAdminsService
from app.bot.filters.group_only import GroupOnlyFilter

router = Router()


@router.message(Command("admins"), GroupOnlyFilter())
@inject
async def admins_cmd(
    message: Message,
    list_admins_service: ListAdminsService = Provide[Container.list_admins_service]
):
    owner, admins = await list_admins_service.get_admins(message.chat.id)

    await message.reply(
        list_admins_service.fmt_admins(owner, admins),
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )