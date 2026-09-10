from enum import StrEnum

class LetterState(StrEnum):
    CORRECT = "correct"
    PRESENT = "present"
    ABSENT = "absent"