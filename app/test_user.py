import asyncio
import random

from app.database.base import DatabaseManager


async def create_fake_users():
    async with DatabaseManager.connect() as db:
        for i in range(1, 21):
            user_id = 9000000000 + i

            await db.execute(
                """
                INSERT OR IGNORE INTO users (
                    user_id,
                    name,
                    money
                )
                VALUES (?, ?, ?)
                """,
                (
                    user_id,
                    f"TestUser_{i}",
                    random.randint(1000, 10000),
                )
            )

            await db.execute("""
            INSERT OR IGNORE INTO ghouls(
                user_id,
                clicks,
                kagune_lvl,
                kagune_was_obtained,
                ghoul_nickname
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                random.randint(10, 500),
                random.randint(100, 5000),
                1,
                f"TestGhoul_{i}",
            )
        )

        await db.commit()


asyncio.run(create_fake_users())