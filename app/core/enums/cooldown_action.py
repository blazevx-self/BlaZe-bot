from enum import Enum

class CooldownAction(str, Enum):
    SNAP = "snap"
    COFFEE = "coffee"
    COFFEE_OVERDOSE = "coffee_overdose"
    QUIZ = "quiz"
    KAGUNE_GROW = "kagune_grow"