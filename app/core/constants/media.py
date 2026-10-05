from pathlib import Path

from app.core.enums.media import MediaCollection, MediaKind

MEDIA_DIR = Path(__file__).resolve().parents[2] / "assets" / "media"

MEDIA_EXTENSIONS = {".mp4"}
VIDEO_COLLECTIONS: set[MediaCollection] = {MediaCollection.EDITS}

KAGUNE_COLLECTIONS: dict[str, MediaCollection] = {
    "укаку": MediaCollection.KAGUNE_UKAKU,
    "коукаку": MediaCollection.KAGUNE_KOUKAKU,
    "ринкаку": MediaCollection.KAGUNE_RINKAKU,
    "бикаку": MediaCollection.KAGUNE_BIKAKU,
}

def media_kind(collection: MediaCollection) -> MediaKind:
    return MediaKind.VIDEO if collection in VIDEO_COLLECTIONS else MediaKind.ANIMATION

# Бот может скачать из Telegram файл не больше 20 МБ
MAX_DOWNLOAD_SIZE = 20 * 1024 * 1024