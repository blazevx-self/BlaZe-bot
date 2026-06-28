from app.database.base import DatabaseManager
from app.database.schemas.users_schemas import CREATE_USERS
from app.database.schemas.ghouls_schemas import CREATE_GHOULS
from app.database.schemas.quiz_schemas import CREATE_QUIZ_TABLE, CREATE_QUIZ_HISTORY_TABLE

async def init_db():
    async with DatabaseManager.connect() as db:
        await db.execute(CREATE_USERS)
        await db.execute(CREATE_GHOULS)
        await db.execute(CREATE_QUIZ_TABLE)
        await db.execute(CREATE_QUIZ_HISTORY_TABLE)

        await db.execute("CREATE INDEX IF NOT EXISTS idx_user_history ON user_quiz_history (user_id, quiz_date)")
        await db.commit()