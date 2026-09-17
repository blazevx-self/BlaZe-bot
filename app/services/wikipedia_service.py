import aiohttp
from urllib.parse import quote

from app.types.services_result.common import WikipediaDescriptionResult
from app.utils.logger import wikipedia_logger

WIKIPEDIA_URL = "https://ru.wikipedia.org/api/rest_v1/page/summary/{title}"
USER_AGENT = "BlaZeBot/1.0"

class WikipediaService:
    """Получает описание слова из русской Википедии."""

    @staticmethod
    async def get_description(word: str) -> WikipediaDescriptionResult | None:
        title = word.strip().capitalize()

        try:
            timeout = aiohttp.ClientTimeout(total=5)

            async with aiohttp.ClientSession(
                timeout=timeout,
                headers={"User-Agent": USER_AGENT}
            ) as session:
                async with session.get(WIKIPEDIA_URL.format(title=quote(title))) as response:
                    if response.status != 200:
                        return None

                    data = await response.json()

        except (aiohttp.ClientError, TimeoutError) as e:
            wikipedia_logger.exception(f"[WIKI] Failed to get description | word={word!r}")
            return None

        description = data.get("extract")

        if not description:
            return None

        if (
            data.get("type") == "disambiguation"
            or "многозначный термин" in description.lower()
        ):
            return None

        return WikipediaDescriptionResult(text=description)