from app.types.time_components import TimeComponents

def parse_seconds(total_seconds: int) -> TimeComponents:
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
    time = parse_seconds(total_seconds)

    parts = []

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