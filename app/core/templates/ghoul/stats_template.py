from app.services.calculate_stats_service import calculate_price, STAT_LIMITS
from app.utils.format_num import format_num

from app.configs.yaml import cfg

# шаблон прокачки характеристик гуля
def stats_text(user: dict, stats: dict) -> str:
    return cfg['message']['stats_text'].format(
        money=format_num(user["money"]),

        strength=stats["strength"],
        agility=stats["agility"],
        speed=stats["speed"],
        hp=stats["hp"],
        regen=stats["regen"],

        p_strength=make_prices_string(stats["strength"], "strength"),
        p_agility=make_prices_string(stats["agility"], "agility"),
        p_speed=make_prices_string(stats["speed"], "speed"),
        p_hp=make_prices_string(stats["hp"], "hp"),
        p_regen=make_prices_string(stats["regen"], "regen"))

def make_prices_string(current_stat: int, stat_name: str) -> str:
    """Форматирование цены статов в сообщении"""
    limit = STAT_LIMITS[stat_name]

    if current_stat >= limit:
        return f"\n└ <code>𝗠𝗔𝗫.</code>"

    p1 = calculate_price(current_stat, 1)
    p3 = calculate_price(current_stat, 3)
    p5 = calculate_price(current_stat, 5)

    return f"\n└ <code>+1: {format_num(p1)}|+3: {format_num(p3)}|+5: {format_num(p5)}</code>"


