from enum import Enum

class LetterState(str, Enum):
    CORRECT = "correct"
    PRESENT = "present"
    ABSENT = "absent"