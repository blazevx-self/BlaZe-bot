CREATE_QUIZ_TABLE = """
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    options TEXT,
    correct TEXT
)
"""

CREATE_QUIZ_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS user_quiz_history (
    user_id INTEGER,
    question_id INTEGER,
    quiz_date TEXT,
    PRIMARY KEY (user_id, question_id, quiz_date)
)
"""