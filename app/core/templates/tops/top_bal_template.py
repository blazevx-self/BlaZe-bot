from aiogram.utils.markdown import html_decoration as hd

from app.configs.yaml import cfg
from app.utils.truncate_name import truncate_text
from app.utils.format_num import format_num


# шаблон топ по балику
def build_top_bal_text(result):
    top_users = result.top_user
    rank = result.rank
    user = result.user

    text = "<b>Топ 15 богатых гулей</b>\n"

    text += "<b>╭─────────────────╮</b>\n"

    prefixes = cfg['message']['tops']['top_money']['prefixes']
    rank_message = cfg['message']['tops']['top_money']['rank_messages']

    for position, top_user in enumerate(top_users, start=1):
        money = format_num(top_user['money'])
        safe_name = hd.quote(truncate_text(top_user['name']))

        prefix = prefixes.get(str(position), f"{position}.")
        name = f"<b>{safe_name}</b>" if position <= 3 else safe_name

        text += f"<b>{prefix}</b> {name} — {money} BlazeCoin\n"

    text += "<b>╰─────────────────╯</b>\n"

    if user.money <= 0:
        text += cfg['message']['tops']['top_money']['rank_messages']['5']

    else:
        message = rank_message.get(str(rank), rank_message['4'])
        text += message.format(rank=rank)

    return text