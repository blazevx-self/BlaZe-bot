def profile_text(
        user_link: str,
        user_id: int,
        status: str,
        money: str,
        registered_at: str,
        race: str,
        days_in_project: int,
        chat_block: str = ""
) -> str:
    return f"""
    <tg-emoji emoji-id=\"6032693626394382504\">👤</tg-emoji> <b>Профиль — {user_link}</b>

<tg-emoji emoji-id=\"5884366771913233289\">✈️</tg-emoji> <b>Id:</b> <code>{user_id}</code>
<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> <b>Раса:</b> <code>{race}</code>  
<tg-emoji emoji-id=\"6041921818896372382\">👋</tg-emoji> <b>Статус:</b> <code>{status}</code>

<tg-emoji emoji-id=\"5258204546391351475\">💵</tg-emoji> <b>Балик:</b> <code>{money} BlazeCoin</code>

<tg-emoji emoji-id=\"5936143551854285132\">📊</tg-emoji> <b>Активность</b>
└ <tg-emoji emoji-id=\"5891211339170326418\">⏳</tg-emoji> <b>В проекте:</b> <code>{days_in_project} дн.</code>
└ <tg-emoji emoji-id=\"5890937706803894250\">📅</tg-emoji> <b>Регистрация:</b> <code>{registered_at}</code>
{chat_block}
"""