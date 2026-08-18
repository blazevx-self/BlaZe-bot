def profile_text(
        user_link: str,
        user_id: int,
        status: str,
        money: str,
        registered_at: str,
        race: str,
        days_in_project: int,
) -> str:
    return f"""
    👤 <b>{user_link} — профиль</b>

🆔 <b>Id:</b> <code>{user_id}</code>
🧬 <b>Раса:</b> <code>{race}</code>
👋 <b>Статус:</b> <code>{status}</code>

💸 <b>Балик:</b> <code>{money} BlazeCoin</code>

📊 <b>Активность</b>
└ ⏳ <b>В проекте:</b> <code>{days_in_project} дн.</code>
└ 📅 <b>Регистрация:</b> <code>{registered_at}</code>
"""