from enum import StrEnum

class ResultStatus(StrEnum):
    """Общие статусы результатов"""
    SUCCESS = "success"
    ERROR = "error"
    COOLDOWN = "cooldown"
    NOT_FOUND = "not_found"
    NOT_ENOUGH_MONEY = "not_enough_money"

    OVERDOSE = "overdose"
    OVERDOSE_COOLDOWN = "overdose_cooldown"
    NOT_ENOUGH_SNAP="not_enough_snap"

    NO_KAGUNE = "no_kagune"

    LIMIT = "limit"
    NO_QUESTIONS = "no_questions"
    LIMIT_REACHED = "limit_reached"

    LOCKED = "locked"
    INVALID_STAT="invalid_stat"
    INVALID_AMOUNT="invalid_amount"
    MAXED="maxed"
