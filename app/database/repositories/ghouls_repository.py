from aiosqlite import Row
from app.database.base import DatabaseManager
from app.core.constants.game.stats import ALLOWED_STATS

# noinspection PyMethodMayBeStatic
class GhoulRepository:
    # КОФЕ
    async def set_coffee_overdose(self, user_id: int, cooldown_timestamp: int) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("""
                UPDATE ghouls SET coffee_cooldown = ?, coffee_session = 0 WHERE user_id = ?
            """, (cooldown_timestamp, user_id))

            await db.commit()

    async def drink_coffee_success(self, user_id: int, amount: int, current_time: int) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("""
                UPDATE users SET money = money + ? WHERE user_id = ?
            """, (amount, user_id))

            await db.execute("""
                UPDATE ghouls SET coffee_total = coffee_total + 1, coffee_last_time = ? WHERE user_id = ?
            """, (current_time, user_id))

            await db.commit()

    # КАГУНЕ
    async def update_kagune_level(self ,user_id: int, new_lvl: int, price: int, timestamp: int) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("""
                UPDATE ghouls SET kagune_lvl = ?, kagune_last_grow = ? WHERE user_id = ?
            """, (new_lvl, timestamp, user_id))

            await db.execute("""
                UPDATE users SET money = money - ? WHERE user_id = ?
            """, (price, user_id))

            await db.commit()

    async def init_kagune(self ,user_id: int, k_type: str) -> None:
        async with DatabaseManager.connect() as db:
            cursor = await db.execute("SELECT kagune_was_obtained FROM ghouls WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()

            if row and row[0]:
                return

            await db.execute("""
                UPDATE ghouls SET kagune_type = ?, kagune_lvl = 1, kagune_was_obtained = 1 WHERE user_id = ?
                AND kagune_was_obtained = 0
            """, (k_type, user_id))

            await db.commit()

    # ЩЕЛК
    async def get_last_click(self, user_id: int) -> int:
        async with DatabaseManager.connect() as db:
            async with db.execute("SELECT last_click FROM ghouls WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row['last_click'] if row else 0

    async def update_last_click(self, user_id: int, timestamp: int) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("UPDATE ghouls SET last_click = ? WHERE user_id = ?", (timestamp, user_id))
            await db.commit()

    async def add_click(self, user_id: int) -> None:
        async with DatabaseManager.connect() as db:
            await db.execute("UPDATE ghouls SET clicks = clicks + 1 WHERE user_id = ?", (user_id,))
            await db.commit()

    # СТАТЫ
    async def get_stats(self, user_id: int) -> None | Row:
        async with DatabaseManager.connect() as db:
            async with db.execute("""
                SELECT strength, agility, speed, hp, regen FROM ghouls WHERE user_id = ?
            """, (user_id,)) as cursor:
                return await cursor.fetchone()

    async def upgrade_stat(self, user_id: int, stat: str, amount: int, price: int) -> bool:
        if stat not in ALLOWED_STATS:
            raise ValueError(f"Unknown strat: {stat}")

        async with DatabaseManager.connect() as db:
            async with db.execute("SELECT money FROM users WHERE user_id = ?", (user_id,)) as cursor:
                user_row = await cursor.fetchone()

                if not user_row or user_row['money'] < price:
                    return False

            await db.execute("UPDATE users SET money = money - ? WHERE user_id = ?", (price, user_id))
            await db.execute(f"UPDATE ghouls SET {stat} = {stat} + ? WHERE user_id = ?", (amount, user_id))
            await db.commit()

            return True

ghouls_repository = GhoulRepository()
