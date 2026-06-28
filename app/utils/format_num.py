def format_num(amount: int | None) -> str:
    """
    Преобразует большое число в компактную строку с суффиксами K/M/B/T.
    Пример: 1500 → '1.5K', 2_500_000 → '2.5M'.
    """
    if amount is None:
        return "0"

    if amount >= 1_000_000_000_000:
        return f"{amount / 1_000_000_000_000:.1f}T"  # 1.0T+
    elif amount >= 1_000_000_000:
        return f"{amount / 1_000_000_000:.1f}B" # 1.0B+
    elif amount >= 1_000_000:
        return f"{amount / 1_000_000:.1f}M"    # 1.0M+
    elif amount >= 1_000:
        return f"{amount / 1_000:.1f}K"        # 1.0K+

    return str(amount)
