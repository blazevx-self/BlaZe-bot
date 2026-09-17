from app.core.constants.game.stats import STAT_LIMITS
from app.types.entities.ghoul import GhoulData

from app.utils.format_num import format_num

def race_profile_text(
    ghoul: GhoulData,
    user_link: str,
    danger_rank: str,
    level: int,
    power: int,
    kagune_lvl: int,
    snap: int,
    coffee: int
) -> str:

    return f"""
     <tg-emoji emoji-id=\"6032693626394382504\">👤</tg-emoji> <b>Расовый профиль — {user_link}</b>

<tg-emoji emoji-id=\"5936143551854285132\">📊</tg-emoji> <b>Уровень гуля:</b> <code>{level}</code>
<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> <b>Ранг опасности:</b> <code>{danger_rank}</code>

<tg-emoji emoji-id=\"5442804822048780010\">😫</tg-emoji> <b>Тип кагуне:</b> <code>{ghoul.kagune_type or 'Нет'}</code>
└ <tg-emoji emoji-id=\"5258391025281408576\">📈</tg-emoji> <b>уровень кагуне:</b> <code>{format_num(kagune_lvl)}</code>

<tg-emoji emoji-id=\"5294078733177611926\">🦠</tg-emoji> <b>RC-клетки:</b> <code>0</code>

<tg-emoji emoji-id=\"5834929920219812289\">💪</tg-emoji> <b>Сила:</b> <code>{format_num(ghoul.strength)}/{STAT_LIMITS['strength']}</code>
<tg-emoji emoji-id=\"5276139556725350230\">🏃‍♀️</tg-emoji> <b>Скорость:</b> <code>{format_num(ghoul.speed)}/{STAT_LIMITS['speed']}</code>
<tg-emoji emoji-id=\"5834678930920969133\">️🦶</tg-emoji> <b>Ловкость:</b> <code>{format_num(ghoul.dexterity)}/{STAT_LIMITS['dexterity']}</code>
<tg-emoji emoji-id=\"5938368005611195877\">❤️</tg-emoji> <b>HP:</b> <code>{format_num(ghoul.hp)}/{STAT_LIMITS['hp']}</code>
<tg-emoji emoji-id=\"5834967608557835277\">❣️</tg-emoji> <b>Регенерация:</b> <code>{ghoul.regen}/{STAT_LIMITS['regen']}</code>

<tg-emoji emoji-id=\"5323761960829862762\">⚡️</tg-emoji> <b>Суммарная мощь:</b> <code>{format_num(power)}</code>

<tg-emoji emoji-id=\"5834596128246469018\">🫰</tg-emoji> <b>Сломано пальцев:</b> <code>{format_num(snap)}</code>
<tg-emoji emoji-id=\"5386470514871003633\">☕️</tg-emoji> <b>Выпито кофе:</b> <code>{format_num(coffee)}</code>

<tg-emoji emoji-id=\"5262604190630314198\">🍖</tg-emoji> <b>Съедено людей:</b> <code>0</code>
<tg-emoji emoji-id=\"5294115682781261925\">🦴</tg-emoji> <b>Съедено гулей:</b> <code>0</code>

<tg-emoji emoji-id=\"5294106989767452474\">🧬</tg-emoji> <b>Какуджа:</b> <code>Нет</code>
"""