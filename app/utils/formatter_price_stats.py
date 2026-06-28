from app.utils.calculate_stats import calculate_price, STAT_LIMITS
from app.utils.format_num import format_num

def make_prices_string(current_stat: int, stat_name: str) -> str:
    """Форматирование цены статов в сообщении"""
    limit = STAT_LIMITS[stat_name]

    if current_stat >= limit:
        return f"\n└ <code>𝗠𝗔𝗫.</code>"

    p1 = calculate_price(current_stat, 1)
    p3 = calculate_price(current_stat, 3)
    p5 = calculate_price(current_stat, 5)

    return f"\n└ <code>+1: {format_num(p1)}|+3: {format_num(p3)}|+5: {format_num(p5)}</code>"


