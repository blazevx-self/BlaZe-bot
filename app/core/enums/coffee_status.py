from enum import StrEnum

class CoffeeStatus(StrEnum):
    SUCCESS = "success"
    NOT_ENOUGH_CLICKS = "not_enough_clicks"
    OVERDOSE = "overdose"
    OVERDOSE_COOLDOWN = "overdose_cooldown"