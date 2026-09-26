from datetime import datetime, timedelta

from app.types.time_components import TimeComponents

def parse_seconds(total_seconds: int) -> TimeComponents:
    """Преобразует общее количество секунд в компоненты времени (
        дни, 
        часы,
        минуты, 
        секунды
    ) и суммарные значения."""
    
    days = total_seconds // (24 * 3600)
    remainder = total_seconds % (24 * 3600)

    hours = remainder // 3600
    remainder = remainder % 3600

    minutes = remainder // 60
    seconds = remainder % 60

    return TimeComponents(
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,

        total_hours=total_seconds // 3600,
        total_minutes=total_seconds // 60,
        total_seconds=total_seconds
    )

def format_duration(total_seconds: int, show_seconds: bool = True) -> str:
    """Форматирует длительность в читаемую строку, например '2ч. и 15мин.'."""
    
    time = parse_seconds(total_seconds)

    parts = []

    if time.days:
        parts.append(f"{time.days}д.")

    if time.hours:
        parts.append(f'{time.hours}ч.')

        if time.minutes:
            parts.append(f'{time.minutes}мин.')

    elif time.minutes:
        parts.append(f'{time.minutes}мин.')

        if show_seconds and time.seconds:
            parts.append(f'{time.seconds}сек.')

    else:
        parts.append(f'{time.seconds}сек.')

    if len(parts) > 1:
        return " и ".join(parts)

    return parts[0]

def days_since_registration(created_at: datetime) -> int:
    """Возвращает количество дней, прошедших с момента регистрации пользователя."""
    return (datetime.now().date() - created_at.date()).days

def parse_duration(value: str | None) -> timedelta | None:
    """'7d', '24h', '30m' -> timedelta. Всё остальное -> None (перманентно)."""

    if not value:
        return None

    units = {"m": "minutes", "h": "hours", "d": "days"}

    if len(value) >= 2 and value[-1] in units and value[:-1].isdigit():
        return timedelta(**{units[value[-1]]: int(value[:-1])})

    return None