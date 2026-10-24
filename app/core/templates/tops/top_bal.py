from aiogram.utils.markdown import html_decoration as hd

from app.configs.yaml_loader import cfg
from app.types.services_result.tops import TopResult

from app.utils.truncate_text import truncate_text
from app.utils.format_num import format_num

def _name(user) -> str:
    return hd.quote(truncate_text(user.name))

def build_top_bal_text(result: TopResult) -> str:
    top_users = result.top_user
    user = result.user
    rank = result.rank

    viewer_money = user.money if result.money is None else result.money

    text = " <tg-emoji emoji-id=\"5258204546391351475\">💵</tg-emoji> <b>Топ 15 богатых гулей</b>\n\n"
    text += "<b>╭─────────────────╮</b>\n"

    prefixes = cfg['message']['tops']['prefixes']
    rank_message = cfg['message']['tops']['top_money']['rank_messages']

    for position, top_user in enumerate(top_users, start=1):
        amount = top_user.user.money if top_user.money is None else top_user.money

        left = _name(top_user.user)
        label = f"{left} + {_name(top_user.partner)}" if top_user.partner else left

        prefix = prefixes.get(str(position), f"{position}.")
        name = f"<b>{label}</b>" if position <= 3 else label

        text += f"<b>{prefix}</b> {name} — {format_num(amount)} BlazeCoin\n"

    text += "<b>╰─────────────────╯</b>\n"

    if viewer_money <= 0:
        text += cfg['message']['tops']['top_money']['not_money']
    else:
        message = rank_message.get(str(rank), rank_message['4'])
        text += message.format(rank=rank)

    return text