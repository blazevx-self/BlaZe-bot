from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.core.constants.game.wordle import WORD_LENGTH
from app.services.game.wordle.wordle_service import WordleService

class WordleGameFilter(BaseFilter):
    """Проверяет, является ли сообщение допустимой попыткой в активной игре Wordle."""

    def __init__(self, wordle_service: WordleService):
        self.wordle_service = wordle_service

    async def __call__(self, message: Message) -> bool:
        if not message.text or not message.from_user:
            return False

        word = message.text.strip()

        if word.startswith('/'):
            return False

        if len(word.split()) != 1:
            return False

        if len(word) != WORD_LENGTH:
            return False

        return self.wordle_service.has_active_game(message.from_user.id)