from app.database.base import DatabaseManager

from app.database.schemas.users_schema import CREATE_USERS
from app.database.schemas.ghouls_schema import CREATE_GHOULS
from app.database.schemas.quiz_schema import CREATE_QUIZ_TABLE, CREATE_QUIZ_HISTORY_TABLE
from app.database.schemas.chat_schema import CREATE_CHAT


async def init_db():
    async with DatabaseManager.connect() as db:
        await db.execute(CREATE_USERS)
        await db.execute(CREATE_GHOULS)
        await db.execute(CREATE_QUIZ_TABLE)
        await db.execute(CREATE_QUIZ_HISTORY_TABLE)
        await db.execute(CREATE_CHAT)

        await db.execute("CREATE INDEX IF NOT EXISTS idx_user_history ON user_quiz_history (user_id, quiz_date)")
        await db.commit()