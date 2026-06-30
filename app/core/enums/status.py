# app/core/enums/status.py
from enum import StrEnum

class ResultStatus(StrEnum):
    """Общие статусы результатов"""
    SUCCESS = "success"
    ERROR = "error"
    COOLDOWN = "cooldown"
    NOT_FOUND = "not_found"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    LOCKED = "locked"

class CoffeeStatus(StrEnum):
    """Статусы кофе"""
    SUCCESS = "success"
    NOT_ENOUGH_CLICKS = "not_enough_clicks"
    OVERDOSE = "overdose"
    OVERDOSE_COOLDOWN = "overdose_cooldown"

class ClickStatus(StrEnum):
    """Статусы кликов"""
    SUCCESS = "success"
    COOLDOWN = "cooldown"

class KaguneStatus(StrEnum):
    """Статусы кагуне"""
    SUCCESS = "success"
    COOLDOWN = "cooldown"
    NOT_ENOUGH_MONEY = "not_enough_money"
    NOT_OPENED = "not_opened"

class QuizStatus(StrEnum):
    """Статусы квиза"""
    SUCCESS = "success"
    LIMIT = "limit"
    NO_QUESTIONS = "no_questions"
    LIMIT_REACHED = "limit_reached"