import asyncio
import subprocess

from datetime import datetime
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile

from app.configs.settings import settings
from app.utils.logger import admin_logger

BACKUP_DIR = Path(settings.BACKUP_DIR)
BACKUP_DIR.mkdir(exist_ok=True)

def _run_pg_dump(path: Path) -> subprocess.CompletedProcess:
    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

    return subprocess.run(
        ["pg_dump", sync_db_url, "-f", str(path), "--no-owner", "--clean", "--if-exists"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )

async def daily_backup(bot: Bot) -> None:
    while True:
        try:
            stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            path = BACKUP_DIR / f"backup_{stamp}.sql"

            proc = await asyncio.to_thread(_run_pg_dump, path)

            if proc.returncode == 0:
                await bot.send_document(
                    chat_id=settings.BACKUP_CHANNEL_ID,
                    document=FSInputFile(path),
                    caption=f"📲 Backup: {path.name}",
                )
            else:
                admin_logger.error(f"[BACKUP] pg_dump error={proc.stderr}")

        except Exception as e:
            admin_logger.exception(f"[BACKUP] failed={e}")

        await asyncio.sleep(86400)