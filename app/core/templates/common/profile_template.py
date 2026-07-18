# Шаблон обычного профиля
def profile_text(
        user_link: str,
        level: int,
        rank: str,
        status: str,
        clicks: str,
        money: str,
        coffee: str
) -> str:
    return f"""
    <tg-emoji emoji-id=\"5316727448644103237\">👤</tg-emoji> <b>{user_link} — обычный профиль</b>

 <tg-emoji emoji-id=\"4994522334992795220\">📊</tg-emoji> <b>Уровень:</b> <code>{level}</code>
 <tg-emoji emoji-id=\"6257870936293251906\">📈</tg-emoji> <b>Ранг:</b> <code>{rank}</code>
 <tg-emoji emoji-id=\"5474613551706429302\">👋</tg-emoji> <b>Статус:</b> <code>{status}</code>

 🫰🏼 <b>Сломано пальцев:</b> {clicks}  
 <tg-emoji emoji-id=\"5864068125112144897\">💸</tg-emoji> <b>Балик:</b> <code>{money} BlazeCoin</code>
 ☕️ <b>Выпито кофе:</b> <code>{coffee}</code>
 
"""
