from app.utils.format_num import format_num
from app.utils.formatter_price_stats import make_prices_string

from app.config import cfg


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