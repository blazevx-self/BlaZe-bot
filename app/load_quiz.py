import json
import aiosqlite
import asyncio
import os
from app.database.database import DB_PATH

async def upload_questions():
    if not os.path.exists('assets/json/quiz.json'):
        print('Файл по пути не найден, чо тупой чтоль?')
        return

    with open('assets/json/quiz.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DROP TABLE IF EXISTS quiz_questions")

        await db.execute('''
                   CREATE TABLE quiz_questions (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       question TEXT,
                       options TEXT,
                       correct TEXT
                   )
               ''')
        await db.commit()

        for q in questions:
            options_str = "|".join(q['options'])
            await db.execute("""
                INSERT INTO quiz_questions (question, options, correct) 
                VALUES (?, ?, ?)
            """, (q['question'], options_str, q['correct']))

        await db.commit()
    print(f"✅ Гатова кароч {len(questions)} вопросов загружено в бдшку.")

if __name__ == "__main__":
    asyncio.run(upload_questions())