CREATE_CHAT = """
    CREATE TABLE IF NOT EXISTS chats (
        chat_id INTEGER PRIMARY KEY,
        creator_id INTEGER,
        title TEXT,
        rules TEXT,
        welcome_message TEXT,
        goodbye_message TEXT,
        created_at DATETIME DEFAULT (datetime('now', 'localtime'))
)
"""