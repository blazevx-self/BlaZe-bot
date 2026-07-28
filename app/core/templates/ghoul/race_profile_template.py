from app.core.constants.game.stats import STAT_LIMITS
from app.types.entities import UserData


# шаблон для расового профиля гуля
def race_profile_text(
    user: UserData,
    user_link: str,
    danger_rank: str,
    level: int,
    power: int,
    kagune_lvl: int
) -> str:

    return f"""
    👤 <b>{user_link}</b> — <b>расовый профиль</b>

🧬 <b>Уровень гуля:</b> <code>{level}</code>
⚠️ <b>ранг опасности:</b> <code>{danger_rank}</code>

👁 <b>Тип кагуне:</b> <code>{user.kagune_type or 'Нет'}</code>
└ 📊 <b>уровень кагуне:</b> <code>{kagune_lvl}</code>

🩸 <b>RC-клетки:</b> <code>0</code>

💪 <b>Сила:</b> <code>{user.strength}/{STAT_LIMITS['strength']}</code>
🏃 <b>Скорость:</b> <code>{user.speed}/{STAT_LIMITS['speed']}</code>
🤸 <b>Ловкость:</b> <code>{user.agility}/{STAT_LIMITS['agility']}</code>
❤️ <b>HP:</b> <code>{user.hp}/{STAT_LIMITS['hp']}</code>
❣ <b>Регенерация:</b> <code>{user.regen}/{STAT_LIMITS['regen']}</code>

⚡ <b>Суммарная мощь:</b> <code>{power}</code>

🥩 <b>Съедено людей:</b> <code>0</code>
🍖 <b>Съедено гулей:</b> <code>0</code>

🧿 <b>Какуджа:</b> <code>Нет</code>

"""