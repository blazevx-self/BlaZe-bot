import random

from app.configs.yaml import cfg
from app.core.templates.game.quiz_template import quiz_result_text

from app.database.repositories.quiz_repository import quiz_repository

from app.core.enums.quiz_status import QuizStatus

# noinspection PyMethodMayBeStatic
class QuizService:
    async def process_quiz_start(self, user: dict):
        user_id = user['user_id']
        access = await quiz_repository.get_quiz_access(user_id)

        # проверка доступных попыток
        if not access['can_play'] or access['left'] <= 0:
            return {"status": QuizStatus.LIMIT}

        questions = await quiz_repository.get_random_questions(user_id=user_id, limit=1)

        if not questions:
            return {"status": QuizStatus.NO_QUESTIONS}

        question = questions[0]

        await quiz_repository.save_quiz_progress(user_id=user_id, question_id=question['id'])

        return {
            "status": QuizStatus.SUCCESS,
            "question": question,
            "left": access['left'] - 1
        }

    async def process_quiz_answer(
            self,
            user: dict,
            question_id: int,
            user_choice: str
    ):

        user_id = user['user_id']
        access = await quiz_repository.get_quiz_access(user_id)

        if not access['can_play'] or access['left'] <= 0:
            return {"status": QuizStatus.LIMIT}

        question = await quiz_repository.get_question_by_id(question_id)
        is_correct = question['correct'].strip().lower() == user_choice.strip().lower()

        reward_min, reward_max = cfg['economy']['quiz']['reward']
        earned = random.randint(reward_min, reward_max) if is_correct else 0

        await quiz_repository.use_question_charge(user_id=user_id, earned_money=earned)

        user['money'] = user.get('money', 0) + earned
        questions_left = access['left'] - 1

        result_text = quiz_result_text(
            question=question['question'],
            correct_answer=question['correct'],
            user_choice=user_choice,
            is_correct=is_correct,
            earned=earned
        )

        if questions_left <= 0:
            return {
                "status": QuizStatus.LIMIT_REACHED,
                "text": result_text,
            }

        return {
            "status": QuizStatus.SUCCESS,
            "text": result_text
        }

quiz_service = QuizService()
