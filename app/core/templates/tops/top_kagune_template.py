from aiogram.utils.markdown import html_decoration as hd

from app.configs.yaml import cfg
from app.utils.format_text import truncate_text
from app.utils.format_num import format_num

# шаблон топ по кагуне
def build_top_kagune_text(result):
    top_users = result.top_user
    user = result.user
    user_rank = result.rank

    text = cfg['message']['tops']['top_kagune']['top_10_text'] + "\n"

    text += "<b>╭─────────────────╮</b>\n"

    prefixes = cfg['message']['tops']['top_kagune']['prefixes']

    for position, top_user in enumerate(top_users, start=1):
        kagune = format_num(top_user['kagune_lvl'])
        safe_name = hd.quote(truncate_text(top_user['ghoul_nickname']))

        prefix = prefixes.get(str(position), f"{position}.")
        name = f"<b>{safe_name}</b>" if position <= 3 else safe_name

        text += f"<b>{prefix}</b> {name} — {kagune}\n"

    text += "<b>╰─────────────────╯</b>\n"

    if user_rank:
        strongest = top_users[0]

        text += cfg['message']['tops']['top_kagune']['top_1_status'].format(
            name=hd.quote(truncate_text(strongest['ghoul_nickname']))
        )

    if user_rank and user_rank > len(top_users):
        text += (
            f"\n<tg-emoji emoji-id=\'5316727448644103237\'>👤</tg-emoji> "
            f"Ты на <b>{user_rank}-м</b> месте — сила твоего кагуне: {format_num(user.kagune_lvl)}"
        )

    return text