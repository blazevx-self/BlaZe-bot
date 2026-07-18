from aiogram.utils.markdown import html_decoration as hd

from app.configs.yaml import cfg
from app.utils.format_text import truncate_text
from app.utils.format_num import format_num

# шаблон топ по щелчкам
def build_top_clicks_text(result):
    top_users = result.top_user
    user = result.user
    user_rank = result.rank

    text = cfg['message']['tops']['top_clicks']['top_20_text'] + "\n"

    text += "<b>╭─────────────────╮</b>\n"

    prefixes = cfg['message']['tops']['top_clicks']['prefixes']

    for position, top_user in enumerate(top_users, start=1):
        clicks = format_num(top_user['clicks'])
        safe_name = hd.quote(truncate_text(top_user['ghoul_nickname']))

        prefix = prefixes.get(str(position), f"{position}.")
        name = f"<b>{safe_name}</b>" if position <= 3 else safe_name

        text += f"<b>{prefix}</b> {name} — {clicks}\n"

    text += "<b>╰─────────────────╯</b>\n"

    if user_rank > len(top_users):
        text += (
            f"\n<tg-emoji emoji-id=\'5316727448644103237\'>👤</tg-emoji> "
            f"Ты на <b>{user_rank}-м</b> месте — сломано пальцев: {format_num(user.clicks)}"
        )

    return text