from app.configs.game import game_cfg

from app.core.templates.game.quiz_template import quiz_result_text
from app.core.enums import ResultStatus

from app.types.entities.user import UserData
from app.types.services_result.game import (
    QuizStartResult,
    QuizAnswerResult
)

from app.database.repositories.quiz_repository import QuizRepository
from app.database.repositories.users_repository import UserRepository

from app.utils.logger import quiz_logger

class QuizService:
    def __init__(self, quiz_repo: QuizRepository, user_repo: UserRepository):
        self.quiz_repo = quiz_repo
        self.user_repo = user_repo

    async def quiz_start(self, user: UserData) -> QuizStartResult:
        """Подготавливает новую викторину для пользователя.

        Проверяет доступные попытки, выбирает случайный вопрос,
        сохраняет прогресс и возвращает данные для отображения.
        """

        user_id = user.telegram_id
        can_play, quiz_question_left = await self.quiz_repo.get_quiz_access(
            telegram_id=user_id,
            daily_limit=game_cfg.quiz.day_limit
        )

        if not can_play or quiz_question_left <= 0:
            quiz_logger.info(f"[QUIZ] Daily limit reached | user_id={user_id}")
            return QuizStartResult(status=ResultStatus.LIMIT)

        questions = await self.quiz_repo.get_random_question(telegram_id=user_id, limit=1)

        if not questions:
            quiz_logger.info(f"[QUIZ] No questions available | user_id={user_id}")
            return QuizStartResult(status=ResultStatus.NO_QUESTIONS)

        question = questions[0]

        quiz_logger.info(
            f"[QUIZ] Question started | user_id={user_id} | "
            f"question_id={question.id} | left={quiz_question_left}"
        )

        return QuizStartResult(
            status=ResultStatus.SUCCESS,
            question=question,
            left=quiz_question_left
        )

    async def quiz_answer(
            self,
            user: UserData,
            question_id: int,
            user_choice: str
    ) -> QuizAnswerResult:
        """Обрабатывает ответ пользователя.

        Проверяет правильность ответа, начисляет награду,
        уменьшает количество попыток и возвращает результат.
        """

        user_id = user.telegram_id
        can_play, quiz_question_left = await self.quiz_repo.get_quiz_access(
            telegram_id=user_id,
            daily_limit=game_cfg.quiz.day_limit
        )

        if not can_play or quiz_question_left <= 0:
            quiz_logger.info(f"[QUIZ] Daily limit reached | user_id={user_id}")
            return QuizAnswerResult(status=ResultStatus.LIMIT)

        question = await self.quiz_repo.get_question_by_id(question_id=question_id)

        if not question:
            quiz_logger.error(f"[QUIZ] Question not found | id={question_id}")
            return QuizAnswerResult(status=ResultStatus.ERROR)

        is_correct = (
            question.correct.strip().lower() == user_choice.strip().lower()
        )

        updated_user = await self.quiz_repo.use_question_charge(telegram_id=user_id)

        if not updated_user:
            return QuizAnswerResult(status=ResultStatus.LIMIT)

        reward = game_cfg.quiz.award if is_correct else 0

        if reward:
            await self.user_repo.change_money(telegram_id=user_id, amount=reward)

        await self.quiz_repo.process_answer(
            telegram_id=user_id,
            question_id=question_id,
            is_correct=is_correct,
            earned=reward
        )

        quiz_logger.info(
            f"[QUIZ] Answer processed | user_id={user_id} | "
            f"question_id={question_id} | correct={is_correct} | earned={reward}"
        )

        result_text = quiz_result_text(
            question=question.question,
            correct_answer=question.correct,
            user_choice=user_choice,
            is_correct=is_correct,
            earned=reward
        )
        
        questions_left = updated_user.quiz_questions_left
        status = ResultStatus.LIMIT_REACHED if questions_left <= 0 else ResultStatus.SUCCESS

        return QuizAnswerResult(
            status=status,
            text=result_text
        )
