from app.database.base import DatabaseManager

from app.types.entities import UserData
from app.database.mappers.user_mapper import row_to_user

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
    async def get_user_by_id(self ,user_id: int) -> UserData | None:
        async with DatabaseManager.connect() as db:
            sql = """
            SELECT 
                u.user_id, u.name, u.username, u.money, u.donate_money, u.is_admin, u.created_at, u.updated_at, u.is_subscribed, u.is_banned, u.ban_reason,u.banned_until,

                g.ghoul_nickname, g.clicks, g.level, g.coffee_total, g.coffee_cooldown, g.coffee_session, g.coffee_last_time,
                g.last_click, g.last_quiz_date, g.quiz_questions_left, g.current_quiz_questions_id,
                g.kagune_type, g.kagune_lvl, g.kagune_last_grow, g.kagune_was_obtained, g.became_ghoul_at,
                g.strength, g.agility, g.speed, g.hp, g.regen
        
            FROM users u        
            JOIN ghouls g ON u.user_id = g.user_id WHERE u.user_id = ?
            """

            async with db.execute(sql, (user_id,)) as cursor:
                row = await cursor.fetchone()

                if not row:
                    return None

                return row_to_user(row)


    async def get_user_by_username(self, username: str) -> UserData | None: 
        async with DatabaseManager.connect() as db: 
            sql = """ 
            SELECT 
                u.user_id, u.name, u.username, u.money, u.donate_money, u.is_admin, u.created_at, u.updated_at, u.is_subscribed, u.is_banned, u.ban_reason, u.banned_until, 
                g.ghoul_nickname, g.clicks, g.level, g.coffee_total, g.coffee_cooldown, g.coffee_session, g.coffee_last_time, 
                g.last_click, g.last_quiz_date, g.quiz_questions_left, g.current_quiz_questions_id, g.kagune_type, g.kagune_lvl, g.kagune_last_grow, g.kagune_was_obtained, 
                g.became_ghoul_at, g.strength, g.agility, g.speed, g.hp, g.regen FROM users u JOIN ghouls g ON u.user_id = g.user_id WHERE u.username = ? 
            """ 
            
            async with db.execute(sql, (username,)) as cursor: 
                row = await cursor.fetchone() 
                return row_to_user(row) if row else None 
                
    async def resolve(self, query: str | int) -> UserData | None: 
        if isinstance(query, int): 
            return await self.get_user_by_id(query) 
            
        q = query.strip() 
        
        if q.lstrip("-").isdigit():
            return await self.get_user_by_id(int(q)) 
                
        return await self.get_user_by_username(q.lstrip('@'))

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

    async def modify_balance(self, user_id: int, amount: int) -> None:
        async with DatabaseManager.connect() as db:
            cursor = await db.execute(
                """
                UPDATE users
                SET money = MAX(0, money + ?)
                WHERE user_id = ?
                RETURNING money
                """, (amount, user_id)
            )
            
            row = await cursor.fetchone()
            await db.commit()

            return row[0]

    async def change_data(self, user_id: int, **kwargs) -> None:
        if not kwargs:
           raise ValueError("No fields to update")

        fields = ", ".join(f"{key} = ?" for key in kwargs)
        values = list(kwargs.values()) + [user_id]

        async with DatabaseManager.connect() as db:
            await db.execute(
                f"UPDATE users SET {fields} WHERE user_id = ?",
                values
            )
            await db.commit()

    # Добавление бабла
    async def add_money(self, user_id: int, amount: int) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("UPDATE users SET money = money + ? WHERE user_id = ?", (amount, user_id))
            await db.commit()

    async def ban(
        self, 
        user_id: int, 
        reason: str | None = None, 
        banned_until: datetime | None = None
    ) -> None: 
        await self.change_data(
            user_id, 
            is_banned=1, 
            ban_reason=reason, 
            banned_until=banned_until.isoformat() if banned_until else None,
        ) 
            
    async def unban(self, user_id: int) -> None: 
        await self.change_data(
            user_id, 
            is_banned=0, 
            ban_reason=None, 
            banned_until=None, 
        )

user_repository = UserRepository()
