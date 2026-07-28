import aiosqlite
from contextlib import asynccontextmanager
from app.core.constants.system.paths import DB_PATH

class DatabaseManager:

        @staticmethod
        @asynccontextmanager
        async def connect():
            db = await aiosqlite.connect(DB_PATH)
            db.row_factory = aiosqlite.Row

            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA foreign_keys=ON")

            try:
                yield db
            finally:
                await db.close()