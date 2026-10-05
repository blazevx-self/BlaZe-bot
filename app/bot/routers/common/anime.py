from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, FSInputFile
from aiogram.utils.chat_action import ChatActionSender

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.configs.yaml_loader import cfg

from app.core.enums import ResultStatus
from app.types.entities.user import UserData

from app.services.common.anime import AnimeService

router = Router()

@router.message(Command("anime"))
@inject
async def anime(
    message: Message,
    command: CommandObject,
    user: UserData,
    anime_service: AnimeService = Provide[Container.anime_service]
):
    texts = cfg['message']['anime']
    args = (command.args or "").split()

    as_gif = bool(args) and args[-1].lower() == "gif"

    if as_gif:
        args = args[:-1]

    if len(args) != 4 or not args[0].isdigit() or not args[1].isdigit():
        await message.reply(texts["usage"])
        return

    season, episode, start, end = args
    progress = await message.reply(texts['cutting'])

    async with ChatActionSender.upload_video(bot=message.bot, chat_id=message.chat.id):
        result = await anime_service.cut(
            user_id=user.telegram_id,
            season=int(season),
            episode=int(episode),
            start=start,
            end=end,
            as_gif=as_gif
        )

    if result.status != ResultStatus.SUCCESS:
        await progress.edit_text(texts[result.status].format(limit=result.limit))
        return

    await progress.edit_text(texts['uploading'])

    caption = texts['caption'].format(season=season, episode=episode, start=start, end=end)
    file = FSInputFile(result.path)

    try:
        if as_gif:
            await message.reply_animation(animation=file, caption=caption)
        else:
            await message.reply_video(video=file, caption=caption, supports_streaming=True)
    finally:
        result.path.unlink(missing_ok=True)

    await progress.delete()