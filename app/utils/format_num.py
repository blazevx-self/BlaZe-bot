def format_num(amount: int | None) -> str:
    """
    Преобразует большое число в компактную строку с суффиксами K/M/B/T.
    Пример: 1500 → '1.5K', 2_500_000 → '2.5M'.
    """

    if amount is None:
        return "0"

    sign = "-" if amount < 0 else ""
    amount = abs(amount)

    if amount >= 1_000_000_000_000_000:
        return f"{sign}{amount / 1_000_000_000_000_000:.1f}Q"

    if amount >= 1_000_000_000_000:
        return f"{sign}{amount / 1_000_000_000_000:.1f}T"

    if amount >= 1_000_000_000:
        return f"{sign}{amount / 1_000_000_000:.1f}B"

    if amount >= 1_000_000:
        return f"{sign}{amount / 1_000_000:.1f}M"

    if amount >= 1_000:
        return f"{sign}{amount / 1_000:.1f}K"

    return f"{sign}{amount}"