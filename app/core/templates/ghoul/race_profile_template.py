from app.core.constants.game.stats import STAT_LIMITS
from app.types.entities.ghoul import GhoulData

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
    👤 <b>{user_link}</b> — <b>расовый профиль</b>

🧬 <b>Уровень гуля:</b> <code>{level}</code>
⚠️ <b>ранг опасности:</b> <code>{danger_rank}</code>

👁 <b>Тип кагуне:</b> <code>{ghoul.kagune_type or 'Нет'}</code>
└ 📊 <b>уровень кагуне:</b> <code>{kagune_lvl}</code>

🩸 <b>RC-клетки:</b> <code>0</code>

💪 <b>Сила:</b> <code>{ghoul.strength}/{STAT_LIMITS['strength']}</code>
🏃 <b>Скорость:</b> <code>{ghoul.speed}/{STAT_LIMITS['speed']}</code>
🤸 <b>Ловкость:</b> <code>{ghoul.dexterity}/{STAT_LIMITS['dexterity']}</code>
❤️ <b>HP:</b> <code>{ghoul.hp}/{STAT_LIMITS['hp']}</code>
❣ <b>Регенерация:</b> <code>{ghoul.regen}/{STAT_LIMITS['regen']}</code>

⚡ <b>Суммарная мощь:</b> <code>{power}</code>

🫰🏼 <b>Сломано пальцев:</b> <code>{snap}</code>
☕️ <b>Выпито кофе:</b> <code>{coffee}</code>

🥩 <b>Съедено людей:</b> <code>0</code>
🍖 <b>Съедено гулей:</b> <code>0</code>

🧿 <b>Какуджа:</b> <code>Нет</code>
"""