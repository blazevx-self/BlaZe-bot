CREATE_GHOULS = """
CREATE TABLE IF NOT EXISTS ghouls (
                user_id INTEGER PRIMARY KEY,
                
                ghoul_nickname TEXT,
                
                clicks INTEGER DEFAULT 0,
                
                level INTEGER DEFAULT 1,
                
                coffee_total INTEGER DEFAULT 0,
                coffee_cooldown INTEGER DEFAULT 0,
                coffee_session INTEGER DEFAULT 0,
                coffee_last_time INTEGER DEFAULT 0,
                
                last_click INTEGER DEFAULT 0,
                last_quiz_date TEXT DEFAULT '',
                
                quiz_questions_left INTEGER DEFAULT 15,
                
                current_quiz_questions_id INTEGER DEFAULT 0,
                
                kagune_type TEXT DEFAULT NULL,
                kagune_lvl INTEGER DEFAULT 0,
                kagune_last_grow INTEGER DEFAULT 0,
                kagune_was_obtained INTEGER DEFAULT 0,
                
                strength INTEGER DEFAULT 1,
                agility INTEGER DEFAULT 1,
                speed INTEGER DEFAULT 1,
                hp INTEGER DEFAULT 1,
                regen INTEGER DEFAULT 1,
                
                became_ghoul_at DATETIME DEFAULT (datetime('now', 'localtime')),
                updated_at DATETIME DEFAULT (datetime('now', 'localtime')),
                
                FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
"""