from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class TimeComponents:
    days: int
    hours: int
    minutes: int
    seconds: int

    total_hours: int
    total_minutes: int
    total_seconds: int