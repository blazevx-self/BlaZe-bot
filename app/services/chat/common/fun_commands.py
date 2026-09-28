import hashlib
import random

from datetime import date, timedelta

from app.configs.yaml_loader import cfg
from app.core.constants.chat.fun_command import (
    OPTIONS_SEPARATOR,
    MAX_OPTIONS,
    MAX_WHEN_DAYS,
    MAX_COUNT,
)

from app.database.repositories.chat.chat_member import ChatMemberRepository
from app.types.entities.user import UserData

class FunService:
    def __init__(self, chat_member_repo: ChatMemberRepository):
        self.chat_member_repo = chat_member_repo

    @staticmethod
    def _daily_random(*parts) -> random.Random:
        """Один и тот же результат для одинаковых данных в течение дня."""

        key = "|".join(str(part).lower() for part in (*parts, date.today()))
        return random.Random(int(hashlib.md5(key.encode()).hexdigest(), 16))

    async def random_member(self, chat_id: int) -> UserData | None:
        return await self.chat_member_repo.get_random_member(chat_id)

    async def random_members(self, chat_id: int, count: int) -> list[UserData]:
        """До `count` разных случайных участников."""

        members: dict[int, UserData] = {}

        for _ in range(count * 3):
            member = await self.random_member(chat_id)

            if not member:
                break

            members[member.telegram_id] = member

            if len(members) == count:
                break

        return list(members.values())

    @staticmethod
    def phrase(key: str, fallback: str, **kwargs) -> str:
        """Случайная фраза из fun.<key> в yaml. Нет ключа — fallback."""

        phrases = cfg.get('message', {}).get('fun', {}).get(key) or [fallback]

        if not phrases or not isinstance(phrases, list):
            phrases = [fallback]

        return random.choice(phrases).format(**kwargs)

    @staticmethod
    def pick_option(options_text: str) -> str | None:
        """'пицца или суши, бургер' -> случайный вариант. Меньше двух -> None."""

        options = [o.strip() for o in OPTIONS_SEPARATOR.split(options_text) if o.strip()]

        if len(options) < 2:
            return None

        return random.choice(options[:MAX_OPTIONS])

    def chance(self, chat_id: int, question: str) -> int:
        return self._daily_random(chat_id, "chance", question).randint(0, 100)

    def how_much(self, chat_id: int, user_id: int, quality: str) -> int:
        """У каждого юзера свой процент на день."""
        return self._daily_random(chat_id, "how_much", user_id, quality).randint(0, 100)

    def rate(self, chat_id: int, subject: str) -> int:
        return self._daily_random(chat_id, "rate", subject).randint(0, 10)

    def count(self, chat_id: int, question: str) -> int:
        return self._daily_random(chat_id, "count", question).randint(0, MAX_COUNT)

    def when(self, chat_id: int, question: str) -> date:
        days = self._daily_random(chat_id, "when", question).randint(1, MAX_WHEN_DAYS)
        return date.today() + timedelta(days=days)