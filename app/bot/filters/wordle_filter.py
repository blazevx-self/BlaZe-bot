from aiogram.filters import BaseFilter
from aiogram.types import Message

from dependency_injector.wiring import Provide

from app.containers import Container
from app.core.constants.game.wordle import WORD_LENGTH

from app.services.game.wordle.wordle_service import WordleService

class WordleGameFilter(BaseFilter):
    """Проверяет, является ли сообщение допустимой попыткой в активной игре Wordle."""

    async def __call__(
        self,
        message: Message,
        wordle_service: WordleService = Provide[Container.wordle_service],
    ) -> bool:
        if not message.text or not message.from_user:
            return False

        word = message.text.strip()

        if word.startswith('/') or len(word.split()) != 1 or len(word) != WORD_LENGTH:
            return False

        return wordle_service.has_active_game(message.from_user.id)