import json
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

from app.core.constants.system.paths import QUIZ_PATH

from app.database.database import session_factory
from app.database.models.quiz import QuizOrm

from app.utils.logger import database_logger

async def seed_quiz_questions() -> None:
    path = Path(QUIZ_PATH)

    if not path.exists():
        database_logger.error(f"[DB] Quiz file not found | path={path}")
        return

    with path.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    async with session_factory() as session:
        for item in questions:
            stmt = insert(QuizOrm).values(
                id=item["id"],
                question=item["question"],
                options=json.dumps(
                    item["options"],
                    ensure_ascii=False
                ),
                correct=item["correct"],
            )

            stmt = stmt.on_conflict_do_update(
                index_elements=[QuizOrm.id],
                set_={
                    "question": stmt.excluded.question,
                    "options": stmt.excluded.options,
                    "correct": stmt.excluded.correct,
                }
            )

            await session.execute(stmt)

        await session.commit()

    database_logger.info(f"[DB] Quiz questions synchronized | count={len(questions)}")