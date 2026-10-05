import random

from aiogram import Bot

from app.core.constants.media import MEDIA_DIR, MEDIA_EXTENSIONS
from app.core.enums.media import MediaCollection

from app.database.repositories.media import MediaRepository
from app.utils.logger import system_logger

class MediaService:
    def __init__(self, media_repo: MediaRepository):
        self.media_repo = media_repo

    async def random(self, collection: MediaCollection) -> tuple[str, str | None] | None:
        """Случайный файл коллекции: (путь, file_id или None)."""

        folder = MEDIA_DIR / collection

        files = [
            file for file in folder.glob("*")
            if file.suffix.lower() in MEDIA_EXTENSIONS
        ] if folder.is_dir() else []

        if not files:
            system_logger.warning(f"[MEDIA] Empty collection | collection={collection}")
            return None

        path = random.choice(files).relative_to(MEDIA_DIR).as_posix()

        return path, await self.media_repo.get_file_id(path)

    async def remember(self, path: str, file_id: str) -> None:
        await self.media_repo.save(path=path, file_id=file_id)

    async def add(
        self,
        bot: Bot,
        file_id: str,
        file_unique_id: str,
        collection: MediaCollection
    ) -> str | None:
        """Скачивает медиа в папку коллекции. None — такое медиа там уже есть."""

        folder = MEDIA_DIR / collection
        folder.mkdir(parents=True, exist_ok=True)

        file = folder / f"{file_unique_id}.mp4"

        if file.exists():
            return None

        await bot.download(file_id, destination=file)

        path = file.relative_to(MEDIA_DIR).as_posix()
        await self.media_repo.save(path=path, file_id=file_id)

        system_logger.info(f"[MEDIA] Added | collection={collection} | path={path}")

        return path