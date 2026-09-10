from datetime import date

from sqlalchemy import select, func, delete, update

from app.database.repositories.base import Base
from app.database.models.quiz import QuizOrm, UserQuizHistoryOrm
from app.database.models.user import UserOrm

class QuizRepository(Base):
    async def get_question_by_id(self, question_id: int) -> QuizOrm:
        stmt = select(QuizOrm).where(QuizOrm.id == question_id)
        return await self.session.scalar(stmt)

    async def get_random_question(self, telegram_id: int, limit: int = 1) -> list[QuizOrm]:
        today = date.today()
        
        used_questions = (
            select(UserQuizHistoryOrm.question_id)
            .where(
                UserQuizHistoryOrm.telegram_id == telegram_id,
                UserQuizHistoryOrm.quiz_date == today          
            )
        )

        stmt = (
            select(QuizOrm)
            .where(~QuizOrm.id.in_(used_questions))
            .order_by(func.random())
            .limit(limit)
        )
        
        result = await self.session.scalars(stmt)
        return list(result)

    async def get_quiz_access(self, telegram_id: int, daily_limit: int) -> tuple[bool, int]:
        user = await self.session.scalar(
            select(UserOrm)
            .where(UserOrm.telegram_id == telegram_id)
        )
        
        if not user:
            return False, 0
        
        today = date.today()
        
        if user.quiz_reset_date != today:
            user.quiz_reset_date = today
            user.quiz_questions_left = daily_limit
            
            await self.session.flush()
            
        return (
            user.quiz_questions_left > 0,
            user.quiz_questions_left
        )

    async def use_question_charge(self, telegram_id: int) -> UserOrm | None:
        stmt = (
            update(UserOrm)
            .where(
                UserOrm.telegram_id == telegram_id,
                UserOrm.quiz_questions_left > 0
            )
            .values(quiz_questions_left=UserOrm.quiz_questions_left - 1)
            .returning(UserOrm)
        )
        
        return await self.session.scalar(stmt)

    async def process_answer(
        self,
        telegram_id: int,
        question_id: int,
        is_correct: bool,
        earned: int
    ) -> UserQuizHistoryOrm | None:
        history = UserQuizHistoryOrm(
            telegram_id=telegram_id,
            question_id=question_id,
            quiz_date=date.today(),
            is_correct=is_correct,
            earned=earned
        )
        
        self.session.add(history)
        await self.session.flush()
        
        return history

    async def clear_old_history(self, telegram_id: int) -> None:
        stmt = delete(UserQuizHistoryOrm).where(
            UserQuizHistoryOrm.telegram_id == telegram_id,
            UserQuizHistoryOrm.quiz_date < date.today()
        )
        await self.session.execute(stmt)