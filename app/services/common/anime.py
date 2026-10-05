import asyncio
import subprocess
import tempfile

from pathlib import Path

from app.core.enums import ResultStatus
from app.core.constants.anime import (
    ANIME_DIR, MAX_VIDEO_SECONDS, MAX_GIF_SECONDS,
    CUT_TIMEOUT, VIDEO_ARGS, GIF_ARGS,
)

from app.types.services_result.common import AnimeClipResult
from app.utils.logger import system_logger

class AnimeService:
    """Нарезка отрывков из серий. Одна нарезка за раз - сервер слабый."""

    def __init__(self):
        self._semaphore = asyncio.Semaphore(1)
        self._busy_users: set[int] = set()

    @staticmethod
    def parse_timecode(text: str) -> int | None:
        """'18:37' -> 1117, '1:02:03' -> 3723. None - неверный формат."""

        parts = text.split(":")

        if not 1 <= len(parts) <= 3 or not all(part.isdigit() for part in parts):
            return None

        if any(int(part) >= 60 for part in parts[1:]):
            return None

        seconds = 0

        for part in parts:
            seconds = seconds * 60 + int(part)

        return seconds

    async def cut(
            self,
            user_id: int,
            season: int,
            episode: int,
            start: str,
            end: str,
            as_gif: bool
    ) -> AnimeClipResult:
        source = ANIME_DIR / f"s{season}e{episode}.mp4"

        if not source.exists():
            return AnimeClipResult(status=ResultStatus.NOT_FOUND)

        start_sec = self.parse_timecode(start)
        end_sec = self.parse_timecode(end)

        if start_sec is None or end_sec is None or end_sec <= start_sec:
            return AnimeClipResult(status=ResultStatus.INVALID_TIME)

        duration = end_sec - start_sec
        limit = MAX_GIF_SECONDS if as_gif else MAX_VIDEO_SECONDS

        if duration > limit:
            return AnimeClipResult(status=ResultStatus.TOO_LONG, limit=limit)

        if user_id in self._busy_users:
            return AnimeClipResult(status=ResultStatus.BUSY)

        self._busy_users.add(user_id)
        output = Path(tempfile.mkstemp(suffix=".mp4")[1])

        try:
            async with self._semaphore:
                success = await self._ffmpeg(source, output, start_sec, duration, as_gif)
        finally:
            self._busy_users.discard(user_id)

        if not success:
            output.unlink(missing_ok=True)
            return AnimeClipResult(status=ResultStatus.ERROR)

        system_logger.info(
            f"[ANIME] Clip cut | user_id={user_id} | s{season}e{episode} | "
            f"{start}-{end} | gif={as_gif}"
        )

        return AnimeClipResult(status=ResultStatus.SUCCESS, path=output)

    @staticmethod
    async def _ffmpeg(
            source: Path,
            output: Path,
            start: int,
            duration: int,
            as_gif: bool
    ) -> bool:
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-v", "error", "-y",
            "-ss", str(start), "-t", str(duration), "-i", str(source),
            *(GIF_ARGS if as_gif else VIDEO_ARGS),
            str(output),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        try:
            _, stderr = await asyncio.wait_for(process.communicate(), timeout=CUT_TIMEOUT)
        except TimeoutError:
            process.kill()

            await process.wait()
            system_logger.warning(f"[ANIME] ffmpeg timeout | source={source.name}")

            return False

        if process.returncode != 0 or output.stat().st_size == 0:
            system_logger.error(f"[ANIME] ffmpeg failed | {stderr.decode(errors='ignore')[-500:]}")
            return False

        return True