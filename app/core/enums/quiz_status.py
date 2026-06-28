from enum import StrEnum

class QuizStatus(StrEnum):
    SUCCESS = "success"
    LIMIT = "limit"
    NO_QUESTIONS = "no_questions"
    LIMIT_REACHED = "limit_reached"