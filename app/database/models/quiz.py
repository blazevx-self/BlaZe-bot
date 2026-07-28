from datetime import datetime

from sqlalchemy import func, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base


class QuizOrm(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    question: Mapped[str] = mapped_column(nullable=False)
    options: Mapped[str] = mapped_column(nullable=False)
    correct_answer: Mapped[str] = mapped_column(nullable=False)

class UserQuizHistoryOrm(Base):
    __tablename__ = "user_quiz_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)

    question_id: Mapped[int] = mapped_column(nullable=False)
    is_correct: Mapped[bool] = mapped_column(default=False)
    earned: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
