from aiosqlite import Row
from app.database.base import DatabaseManager

# noinspection PyMethodMayBeStatic
class TopsRepository:
    async def get_top(self, top_type: str, limit: int) -> list[Row]:
        async with DatabaseManager.connect() as db:
            if top_type == "money":
                sql = """
                    SELECT user_id, name, money FROM users WHERE money > 0 ORDER BY money DESC LIMIT ?
                """

            elif top_type == "clicks":
                sql = """
                    SELECT user_id, ghoul_nickname, clicks FROM ghouls WHERE clicks > 0 ORDER BY clicks DESC LIMIT ?
                """

            elif top_type == "kagune":
                sql = """
                    SELECT user_id, ghoul_nickname, kagune_lvl FROM ghouls WHERE kagune_lvl > 0 ORDER BY kagune_lvl DESC LIMIT ?
                """

            else:
                raise ValueError(f"Unknown top type: {top_type}")

            async with db.execute(sql, (limit,)) as cursor:
                return await cursor.fetchall()

    async def get_rank(self, user_id: int, top_type: str) -> int | None:
        async with DatabaseManager.connect() as db:
            if top_type == "money":
                sql = """
                    WITH ranked AS (
                        SELECT 
                            user_id, 
                            RANK() OVER 
                        (ORDER BY money DESC) AS rank 
                            FROM users WHERE money > 0
                    )
                    SELECT rank FROM ranked WHERE user_id = ?
                """

            elif top_type == "clicks":
                sql = """
                    WITH ranked AS (
                        SELECT 
                            user_id, 
                            RANK() OVER 
                        (ORDER BY clicks DESC) AS rank 
                            FROM ghouls WHERE clicks > 0
                    )
                    SELECT rank FROM ranked WHERE user_id = ?
                """

            elif top_type == "kagune":
                sql = """
                    WITH ranked AS (
                        SELECT 
                            user_id, 
                            RANK() OVER 
                        (ORDER BY kagune_lvl DESC) AS rank 
                            FROM ghouls WHERE kagune_lvl > 0 
                    )
                    SELECT rank FROM ranked WHERE user_id = ?
                """

            else:
                raise ValueError(f"Unknown top type: {top_type}")

            async with db.execute(sql, (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row['rank'] if row else None


tops_repository = TopsRepository()