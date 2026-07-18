import random

from app.configs.game import game_cfg

from app.core.templates.game.quiz_template import quiz_result_text
from app.core.enums import ResultStatus

from app.types.entities import UserData
from app.types.services_types.game import (
    QuizStartResult,
    QuizAnswerResult
)

from app.database.repositories.quiz_repository import quiz_repository
from app.utils.logger import quiz_logger

# noinspection PyMethodMayBeStatic
class QuizService:
    """Сервис логики викторины."""

    async def process_quiz_start(self, user: UserData) -> QuizStartResult:
        """Подготавливает новую викторину для пользователя.

        Проверяет доступные попытки, выбирает случайный вопрос,
        сохраняет прогресс и возвращает данные для отображения.
        """

        user_id = user.user_id
        access = await quiz_repository.get_quiz_access(user_id)

        if not access['can_play'] or access['left'] <= 0:
            quiz_logger.info(f"[QUIZ] Daily limit reached | user_id={user_id}")
            return QuizStartResult(status=ResultStatus.LIMIT)

        questions = await quiz_repository.get_random_questions(user_id=user_id, limit=1)

        if not questions:
            quiz_logger.info(f"[QUIZ] No questions available | user_id={user_id}")
            return QuizStartResult(status=ResultStatus.NO_QUESTIONS)

        question = questions[0]

        await quiz_repository.save_quiz_progress(user_id=user_id, question_id=question['id'])

        quiz_logger.info(
            f"[QUIZ] Question started | user_id={user_id} | "
            f"question_id={question['id']} | left={access['left'] - 1}"
        )

        return QuizStartResult(
            status=ResultStatus.SUCCESS,
            question=question,
            left=access['left'] - 1
        )

    async def process_quiz_answer(
            self,
            user: UserData,
            question_id: int,
            user_choice: str
    ) -> QuizAnswerResult:
        """Обрабатывает ответ пользователя.

        Проверяет правильность ответа, начисляет награду,
        уменьшает количество попыток и возвращает результат.
        """

        user_id = user.user_id
        access = await quiz_repository.get_quiz_access(user_id)

        if not access['can_play'] or access['left'] <= 0:
            quiz_logger.info(f"[QUIZ] Daily limit reached | user_id={user_id}")
            return QuizAnswerResult(status=ResultStatus.LIMIT)

        question = await quiz_repository.get_question_by_id(question_id)
        is_correct = question['correct'].strip().lower() == user_choice.strip().lower()

        reward_min, reward_max = game_cfg.quiz.reward
        earned = random.randint(reward_min, reward_max) if is_correct else 0

        await quiz_repository.use_question_charge(user_id=user_id, earned_money=earned)

        quiz_logger.info(
            f"[QUIZ] Answer processed | user_id={user_id} | "
            f"question_id={question_id} | correct={is_correct} | earned={earned}"
        )

        new_money = user.money + earned
        questions_left = access['left'] - 1

        result_text = quiz_result_text(
            question=question['question'],
            correct_answer=question['correct'],
            user_choice=user_choice,
            is_correct=is_correct,
            earned=earned
        )

        status = ResultStatus.LIMIT_REACHED if questions_left <= 0 else ResultStatus.SUCCESS

        return QuizAnswerResult(
            status=status,
            text=result_text,
            new_money=new_money
        )

quiz_service = QuizService()
