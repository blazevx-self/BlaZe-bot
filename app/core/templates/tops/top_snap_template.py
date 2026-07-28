from aiogram.utils.markdown import html_decoration as hd

from app.configs.yaml import cfg
from app.utils.truncate_name import truncate_text
from app.utils.format_num import format_num

# шаблон топ по щелчкам
def build_top_snap_text(result):
    top_users = result.top_user
    user = result.user
    user_rank = result.rank

    text = "<b>Топ 20 сломанных пальцев</b>\n"

    text += "<b>╭─────────────────╮</b>\n"

    prefixes = cfg['message']['tops']['top_snap']['prefixes']

    for position, top_user in enumerate(top_users, start=1):
        snap = format_num(top_user['clicks'])
        safe_name = hd.quote(truncate_text(top_user['ghoul_nickname']))

        prefix = prefixes.get(str(position), f"{position}.")
        name = f"<b>{safe_name}</b>" if position <= 3 else safe_name

        text += f"<b>{prefix}</b> {name} — {snap}\n"

    text += "<b>╰─────────────────╯</b>\n"

    if user_rank == 0:
        text += (
            f"\n<b>Ты не входишь в топ сломанных пальцев. Воспользуйся командой «щелк»</b>"
        )

    if user_rank > len(top_users):
        text += (
            f"\n<tg-emoji emoji-id=\'5316727448644103237\'>👤</tg-emoji> "
            f"Ты на <b>{user_rank}-м</b> месте — сломано пальцев: {format_num(user.snap)}"
        )

    return text