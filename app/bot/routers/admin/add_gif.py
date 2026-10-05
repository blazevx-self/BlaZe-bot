from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.configs.yaml_loader import cfg

from app.core.constants.media import MAX_DOWNLOAD_SIZE
from app.core.enums.media import MediaCollection

from app.services.media import MediaService
from app.bot.filters.admin import AdminFilter

router = Router()

@router.message(Command("add_gif"), AdminFilter())
@inject
async def add_gif(
    message: Message,
    command: CommandObject,
    media_service: MediaService = Provide[Container.media_service]
):
    texts = cfg["message"]["media"]
    reply = message.reply_to_message
    media = reply and (reply.animation or reply.video)

    if not media:
        await message.reply(texts["no_media"])
        return

    try:
        collection = MediaCollection((command.args or "").strip().lower())
    except ValueError:
        names = ", ".join(f"<code>{collection}</code>" for collection in MediaCollection)
        await message.reply(texts['no_collection'].format(collections=names))
        return

    if media.file_size and media.file_size > MAX_DOWNLOAD_SIZE:
        await message.reply(texts['too_big'])
        return

    path = await media_service.add(
        bot=message.bot,
        file_id=media.file_id,
        file_unique_id=media.file_unique_id,
        collection=collection
    )

    if path is None:
        await message.reply(texts["already_exists"])
        return

    await message.reply(texts["added"].format(collection=collection, path=path))