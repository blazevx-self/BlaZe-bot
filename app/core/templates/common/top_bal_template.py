from app.configs.yaml import cfg

from aiogram.utils.markdown import html_decoration as hd
from app.utils.format_num import format_num

# шалон топ по балику
def build_top_text(data: dict) -> str:
    top_users = data["top_users"]
    rank = data["rank"]
    user = data["user"]

    text = cfg['message']['tops']['top_15_text'] + "\n"

    prefixes = cfg['message']['tops']['prefixes']
    rank_message = cfg['message']['tops']['rank_messages']

    for position, top_user in enumerate(top_users, start=1):
        money = format_num(top_user['money'])
        safe_name = hd.quote(top_user["name"])

        prefix = prefixes.get(str(position), f"{position}.")
        name = f"<b>{safe_name}</b>" if position <= 3 else safe_name

        text += f"<b>{prefix}</b> {name} — {money} BlazeCoin\n"

    text += "<b>╰─────────────────╯</b>\n"

    if user["money"] <= 0:
        text += cfg['message']['tops']['rank_messages']["5"]
    elif str(rank) in rank_message:
        text += rank_message[str(rank)]
    else:
        text += rank_message.get(str(rank)), rank_message["4"].format(rank=rank)

    return text