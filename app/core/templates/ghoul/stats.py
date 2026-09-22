from app.configs.yaml_loader import cfg

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.services.ghouls.stats.calculate_stats import calculate_price, STAT_LIMITS
from app.utils.format_num import format_num

def stats_text(user: UserData, ghoul: GhoulData) -> str:
    return cfg['message']['stats']['stats_text'].format(
        money=format_num(user.money),

        strength=ghoul.strength,
        dexterity=ghoul.dexterity,
        speed=ghoul.speed,
        hp=ghoul.hp,
        regen=ghoul.regen,

        p_strength=make_prices_string(ghoul.strength, "strength"),
        p_dexterity=make_prices_string(ghoul.dexterity, "dexterity"),
        p_speed=make_prices_string(ghoul.speed, "speed"),
        p_hp=make_prices_string(ghoul.hp, "hp"),
        p_regen=make_prices_string(ghoul.regen, "regen")
    )

def make_prices_string(current_stat: int, stat_name: str) -> str:
    """Форматирование цены статов в сообщении"""
    limit = STAT_LIMITS[stat_name]

    if current_stat >= limit:
        return f"\n└ <code>𝗠𝗔𝗫.</code>"

    p1 = calculate_price(stat_name, current_stat, 1)
    p3 = calculate_price(stat_name, current_stat, 3)
    p5 = calculate_price(stat_name, current_stat, 5)

    return f"\n└ <code>+1: {format_num(p1)}|+3: {format_num(p3)}|+5: {format_num(p5)}</code>"