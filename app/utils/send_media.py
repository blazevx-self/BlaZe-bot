from collections.abc import Awaitable, Callable

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    Message, FSInputFile, InlineKeyboardMarkup,
    InputMediaAnimation, InputMediaVideo
)

from app.core.constants.media import MEDIA_DIR, media_kind
from app.core.enums.media import MediaCollection, MediaKind
from app.services.media import MediaService

Source = str | FSInputFile

async def _deliver(
    collection: MediaCollection,
    media_service: MediaService,
    send: Callable[[Source], Awaitable[Message | bool]],
) -> Message | bool | None:
    """Отправляет случайное медиа коллекции по file_id, а если его нет или он протух — файлом.
    Новый file_id запоминает. None — коллекция пустая."""

    media = await media_service.random(collection)

    if media is None:
        return None

    path, file_id = media
    file = FSInputFile(MEDIA_DIR / path)

    try:
        sent = await send(file_id or file)
    except TelegramBadRequest:
        if not file_id:
            raise

        sent = await send(file)

    if isinstance(sent, Message):
        uploaded = sent.animation or sent.video or sent.document

        if uploaded and uploaded.file_id != file_id:
            await media_service.remember(path=path, file_id=uploaded.file_id)

    return sent

async def reply_media(
    message: Message,
    collection: MediaCollection,
    media_service: MediaService,
    caption: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Ответ новым сообщением с медиа."""

    is_video = media_kind(collection) == MediaKind.VIDEO

    async def send(source: Source) -> Message:
        if is_video:
            return await message.reply_video(video=source, caption=caption, reply_markup=reply_markup)

        return await message.reply_animation(animation=source, caption=caption, reply_markup=reply_markup)

    if await _deliver(collection, media_service, send) is None:
        await message.reply(text=caption, reply_markup=reply_markup)

async def edit_media(
    message: Message,
    collection: MediaCollection,
    media_service: MediaService,
    caption: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Замена медиа в уже отправленном сообщении (для колбэков)."""

    input_media = InputMediaVideo if media_kind(collection) == MediaKind.VIDEO else InputMediaAnimation

    async def send(source: Source) -> Message | bool:
        return await message.edit_media(
            media=input_media(media=source, caption=caption),
            reply_markup=reply_markup
        )

    if await _deliver(collection, media_service, send) is not None:
        return

    # Коллекция пустая - меняем только текст
    if message.text:
        await message.edit_text(text=caption, reply_markup=reply_markup)
    else:
        await message.edit_caption(caption=caption, reply_markup=reply_markup)