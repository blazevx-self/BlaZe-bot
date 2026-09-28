import asyncio
import aiohttp

from datetime import date
from cachetools import TTLCache
from pydantic import SecretStr

from app.core.constants.chat.ai import (
    AI_BASE_URL,
    AI_TIMEOUT_SECONDS,
    AI_MAX_TOKENS,
    AI_TEMPERATURE,
    AI_MAX_QUESTION_LENGTH,
    AI_USER_COOLDOWN_SECONDS,
    AI_MAX_CONCURRENT,
    AI_SYSTEM_PROMPT,
    AI_DAILY_LIMIT
)
from app.utils.logger import bot_logger

class AIChatService:
    def __init__(self, api_key: SecretStr | None, model: str) -> None:
        self._api_key = api_key.get_secret_value() if api_key else None
        self._model = model
        self._session: aiohttp.ClientSession | None = None
        self._semaphore = asyncio.Semaphore(AI_MAX_CONCURRENT)
        self._cooldowns = TTLCache(maxsize=10_000, ttl=AI_USER_COOLDOWN_SECONDS)
        self._daily_date = date.today()
        self._daily_count = 0

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    def try_acquire(self, user_id: int) -> bool:
        if user_id in self._cooldowns:
            return False

        today = date.today()

        if today != self._daily_date:
            self._daily_date, self._daily_count = today, 0

        if self._daily_count >= AI_DAILY_LIMIT:
            return False

        self._daily_count += 1
        self._cooldowns[user_id] = True

        return True

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                base_url=AI_BASE_URL,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=aiohttp.ClientTimeout(total=AI_TIMEOUT_SECONDS)
            )

        return self._session

    async def ask(
        self,
        question: str,
        user_name: str,
        context: str | None = None
    ) -> str | None:
        """Ответ нейросети или None при любой ошибке (тогда отвечает шар)."""

        if not self.enabled:
            return None

        messages = [{"role": "system", "content": AI_SYSTEM_PROMPT}]

        if context:
            messages.append({"role": "assistant", "content": context})

        messages.append({"role": "user", "content": f"{user_name}: {question[:AI_MAX_QUESTION_LENGTH]}"})

        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": AI_MAX_TOKENS,
            "temperature": AI_TEMPERATURE,
        }

        try:
            async with self._semaphore:
                async with self._get_session().post("/chat/completions", json=payload) as response:
                    if response.status != 200:
                        bot_logger.warning(
                            f"[AI] Bad status | status={response.status} | "
                            f"body={(await response.text())[:200]}"
                        )
                        return None

                    data = await response.json()

            return data["choices"][0]["message"]["content"].strip() or None

        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, IndexError, TypeError) as e:
            bot_logger.warning(f"[AI] Request failed | error={e!r}")
            return None

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()