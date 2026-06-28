from aiosqlite import Row
from app.database.base import DatabaseManager

# noinspection PyMethodMayBeStatic

class UserRepository:
    # Создание юзера
    async def create_user(self ,user_id: int, name: str, username: str |None):
        async with DatabaseManager.connect() as db:
            await db.execute("""
                INSERT OR IGNORE INTO users (user_id, name, username) VALUES (?, ?, ?)
            """, (user_id, name, username))
            await db.execute("""
                INSERT OR IGNORE INTO ghouls (user_id, ghoul_nickname) VALUES (?, ?)
            """, (user_id, name))

            await db.commit()

    # ID юзера
    async def get_user_by_id(self ,user_id: int) -> dict | None:
        async with DatabaseManager.connect() as db:
            sql = """
            SELECT 
                u.user_id, u.name, u.username, u.money, u.donate_money, u.is_admin, u.created_at, u.updated_at, u.is_subscribed,
            
                g.ghoul_nickname, g.clicks, g.level, g.coffee_total, g.coffee_cooldown, g.coffee_session, g.coffee_last_time,
                g.last_click, g.last_quiz_date, g.quiz_questions_left, g.current_quiz_questions_id,
                g.kagune_type, g.kagune_lvl, g.kagune_last_grow, g.kagune_was_obtained, g.became_ghoul_at,
                g.strength, g.agility, g.speed, g.hp, g.regen
        
            FROM users u        
            JOIN ghouls g ON u.user_id = g.user_id WHERE u.user_id = ?
            """

            async with db.execute(sql, (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    # Бонус (подписка на канал)
    async def activate_subscribed_bonus(self ,user_id: int, bonus: int) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("UPDATE users SET money = money + ?, is_subscribed = 1 WHERE user_id = ?", (bonus, user_id))
            await db.commit()

    # Обновление ника и юзернейм в двух таблицах
    async def update_user_data(self ,user_id: int, name: str, username: str | None) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("""
                UPDATE users SET name = ?, username = ? WHERE user_id = ?
            """, (name, username, user_id))

            await db.execute("""
                UPDATE ghouls SET ghoul_nickname = ? WHERE user_id = ?
            """, (name, user_id))

            await db.commit()

    # Добавление бабла
    async def add_money(self ,user_id: int, amount: int) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("UPDATE users SET money = money + ? WHERE user_id = ?", (amount, user_id))
            await db.commit()

    # ТОП
    async def get_user_top(self ,limit: int = 15) -> list[Row]:
        async with DatabaseManager.connect() as db:
            sql = "SELECT user_id, name, money FROM users WHERE money > 0 ORDER BY money DESC LIMIT ?"

            async with db.execute(sql, (limit,)) as cursor:
                return await cursor.fetchall()

    async def get_user_rank(self, user_id: int) -> int:
        async with DatabaseManager.connect() as db:
            sql = """
                WITH ranked_users AS (SELECT user_id, ROW_NUMBER() OVER (ORDER BY money DESC) as rank FROM users)
                SELECT rank FROM ranked_users WHERE user_id = ?
            """

            async with db.execute(sql, (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row['rank'] if row else None

user_repository = UserRepository()