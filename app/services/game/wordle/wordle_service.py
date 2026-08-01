from __future__ import annotations

import random

from pathlib import Path

from app.configs.game import game_cfg
from app.core.constants.game.wordle import WORD_LENGTH
from app.core.constants.system.paths import WORDLE_WORDS_PATH
from app.core.enums.letterstate import LetterState

from app.types.entities import UserData
from app.types.services_result.game import GuessResult, WordleResult
from app.types.services_result.game import WordleSession

from app.services.game.wordle.renderer import render_board
from app.database.repositories.users_repository import user_repository

from app.utils.logger import wordle_logger

class WordleService:
    def __init__(self) -> None:
        self._sessions: dict[int, WordleSession] = {}
        self._words = self._load_words()


    @staticmethod
    def _load_words() -> list[str]:
        path = Path(WORDLE_WORDS_PATH)
        return [
            word.strip().upper()
            for word in path.read_text(encoding="utf-8").splitlines()
            if len(word.strip()) == WORD_LENGTH
        ]


    @staticmethod
    def _validate_word(word: str) -> str:
        word = word.upper().strip()

        if len(word) != WORD_LENGTH:
            raise ValueError(f"Слово должно содержать {WORD_LENGTH} букв.")

        if not word.isalpha():
            raise ValueError("Допустимы только буквы.")

        return word


    @staticmethod
    def _calculate_states(target: str, word: str) -> list[LetterState]:
        states = [LetterState.ABSENT] * WORD_LENGTH
        remaining: dict[str, int] = {}

        for i in range(WORD_LENGTH):
            if word[i] == target[i]:
                states[i] = LetterState.CORRECT
            else:
                remaining[target[i]] = remaining.get(target[i], 0) + 1

        for i in range(WORD_LENGTH):
            if states[i] == LetterState.CORRECT:
                continue

            if remaining.get(word[i], 0) > 0:
                states[i] = LetterState.PRESENT
                remaining[word[i]] -= 1

        return states


    def start_game(self, telegram_id: int) -> bytes:
        session = WordleSession(target_word=random.choice(self._words))
        self._sessions[telegram_id] = session
        wordle_logger.info(f"[WORDLE] Game started | user_id={telegram_id}")
        return render_board(session.guesses)


    def has_active_game(self, telegram_id: int) -> bool:
        session = self._sessions.get(telegram_id)
        return session is not None and not session.is_game_over


    def get_board(self, telegram_id: int) -> bytes | None:
        session = self._sessions.get(telegram_id)

        if not session:
            return None

        return render_board(session.guesses)


    def finish_game(self, telegram_id: int) -> str | None:
        session = self._sessions.pop(telegram_id, None)
        return session.target_word if session else None


    async def make_guess(
        self,
        telegram_id: int,
        word: str,
        user: UserData,
    ) -> WordleResult | None:

        session = self._sessions.get(telegram_id)

        if not session or session.is_game_over:
            return None

        word = self._validate_word(word)
        states = self._calculate_states(session.target_word, word)

        guess = GuessResult(word=word, states=states)
        session.guesses.append(guess)

        wordle_logger.info(
            f"[WORDLE] Guess | user_id={user.user_id} | "
            f"word={word} | attempts={session.attempts_used}"
        )

        is_game_over = session.is_game_over
        image = render_board(session.guesses)

        earned = 0
        new_money = None

        if is_game_over:
            if session.is_win:
                reward_min, reward_max = game_cfg.wordle.reward
                earned = random.randint(reward_min, reward_max)

                wordle_logger.info(
                    f"[WORDLE] Win | user_id={user.user_id} | "
                    f"attempts={session.attempts_used} | earned={earned}"
                )

                await user_repository.add_money(user_id=user.user_id, amount=earned)
                new_money = user.money + earned

                wordle_logger.info(
                    f"[WORDLE] Reward applied | user_id={user.user_id} | "
                    f"amount={earned} | new_money={new_money}"
                )

            else:
                wordle_logger.info(f"[WORDLE] Loss | user_id={user.user_id} | attempts={session.attempts_used}")

            self._sessions.pop(telegram_id, None)

        return WordleResult(
            image=image,
            guess=guess,
            attempts_used=session.attempts_used,
            attempts_left=session.attempts_left,
            is_win=session.is_win,
            is_game_over=session.is_game_over,
            target_word=session.target_word if session.is_game_over else None,
            board_message_id=session.board_message_id,
            earned=earned,
            new_money=new_money,
        )


    def set_board_message_id(self, telegram_id: int, message_id: int) -> None:
        session = self._sessions.get(telegram_id)
        if session:
            session.board_message_id = message_id


    def get_board_message_id(self, telegram_id: int) -> int | None:
        session = self._sessions.get(telegram_id)
        return session.board_message_id if session else None

wordle_service = WordleService()