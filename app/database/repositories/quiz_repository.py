from datetime import datetime
from app.database.base import DatabaseManager
from aiosqlite import Row

# noinspection PyMethodMayBeStatic
class QuizRepository:
    async def get_quiz_access(self, user_id: int) -> dict:
        async with DatabaseManager.connect() as db:
            today = datetime.now().strftime('%Y-%m-%d')

            async with db.execute("SELECT last_quiz_date, quiz_questions_left, current_quiz_questions_id FROM ghouls WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()

                if not row:
                    return {
                        "can_play": False,
                        "left": 0,
                        "current": 0
                    }

                if row['last_quiz_date'] != today:
                    await db.execute("UPDATE ghouls SET last_quiz_date = ?, quiz_questions_left = 15 WHERE user_id = ?", (today, user_id,))
                    await db.execute("DELETE FROM user_quiz_history WHERE user_id = ?", (user_id,))
                    await db.commit()

                    return {
                        "can_play": True,
                        "left": 15,
                        "current": 0
                    }

                return {
                    "can_play": row['quiz_questions_left'] > 0,
                    "left": row['quiz_questions_left'],
                    "current": row['current_quiz_questions_id']
                }

    async def use_question_charge(self, user_id: int, earned_money: int):
        async with DatabaseManager.connect() as db:
            await db.execute('UPDATE users SET money = money + ? WHERE user_id = ?', (earned_money, user_id))
            await db.execute('UPDATE ghouls SET quiz_questions_left = quiz_questions_left - 1 WHERE user_id = ?', (user_id,))
            await db.commit()

    async def get_random_questions(self, user_id: int, limit: int = 1) -> list[Row]:
        async with DatabaseManager.connect() as db:
            today = datetime.now().strftime('%Y-%m-%d')

            sql = """
                SELECT * FROM quiz_questions 
                WHERE id NOT IN (
                    SELECT question_id FROM user_quiz_history 
                    WHERE user_id = ? AND quiz_date = ?
                ) 
                ORDER BY RANDOM() LIMIT ?
            """

            async with db.execute(sql, (user_id, today, limit)) as cursor:
                return await cursor.fetchall()

    async def get_question_by_id(self, question_id: int) -> Row | None:
        async with DatabaseManager.connect() as db:
            async with db.execute("SELECT * FROM quiz_questions WHERE id = ?", (question_id,)) as cursor:
                return await cursor.fetchone()

    async def save_quiz_progress(self, user_id: int, question_id: int):
        async with DatabaseManager.connect() as db:
            today = datetime.now().strftime('%Y-%m-%d')

            await db.execute("INSERT OR IGNORE INTO user_quiz_history (user_id, question_id, quiz_date) VALUES (?, ?, ?)", (user_id,question_id, today))
            await db.execute("UPDATE ghouls SET current_quiz_questions_id = ? WHERE user_id = ?", (question_id, user_id))
            await db.commit()

quiz_repository = QuizRepository()