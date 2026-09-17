from aiogram.utils.markdown import html_decoration as hd

from app.configs.yaml_loader import cfg
from app.types.services_result.tops import TopResult

from app.utils.truncate_name import truncate_text
from app.utils.format_num import format_num

def build_top_bal_text(result: TopResult) -> str:
    top_users = result.top_user
    user = result.user
    rank = result.rank

    text = " <tg-emoji emoji-id=\"5258204546391351475\">💵</tg-emoji> <b>Топ 15 богатых гулей</b>\n\n"
    text += "<b>╭─────────────────╮</b>\n"

    prefixes = cfg['message']['tops']['prefixes']
    rank_message = cfg['message']['tops']['top_money']['rank_messages']

    for position, top_user in enumerate(top_users, start=1):
        money = format_num(top_user.user.money)
        safe_name = hd.quote(truncate_text(top_user.user.name))

        prefix = prefixes.get(str(position), f"{position}.")
        name = f"<b>{safe_name}</b>" if position <= 3 else safe_name

        text += f"<b>{prefix}</b> {name} — {money} BlazeCoin\n"

    text += "<b>╰─────────────────╯</b>\n"

    if user.money <= 0:
        text += cfg['message']['tops']['top_money']['not_money']

    else:
        message = rank_message.get(str(rank), rank_message['4'])
        text += message.format(rank=rank)

    return text