from enum import StrEnum

class KaguneStatus(StrEnum):
    SUCCESS = "success"
    COOLDOWN = "cooldown"
    NOT_ENOUGH_MONEY = "not_enough_money"
    NOT_OPENED = "not_opened"

