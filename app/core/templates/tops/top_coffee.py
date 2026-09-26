from aiogram.utils.markdown import html_decoration as hd

from app.configs.yaml_loader import cfg
from app.types.services_result.tops import TopResult

from app.utils.truncate_text import truncate_text
from app.utils.format_num import format_num

def build_top_coffee_text(result: TopResult) -> str:
    top_users = result.top_user
    ghoul = result.ghoul
    user_rank = result.rank

    text = "<tg-emoji emoji-id=\"5386470514871003633\">☕️</tg-emoji> <b>Топ 20 гулей по выпитому кофе</b>\n\n"
    text += "<b>╭─────────────────╮</b>\n"

    prefixes = cfg['message']['tops']['prefixes']

    for position, top_user in enumerate(top_users, start=1):
        coffee = format_num(top_user.ghoul.coffee_count)
        safe_name = hd.quote(truncate_text(top_user.user.name))

        prefix = prefixes.get(str(position), f"{position}.")
        name = f"<b>{safe_name}</b>" if position <= 3 else safe_name

        text += f"<b>{prefix}</b> {name} — {coffee} выпито\n"

    text += "<b>╰─────────────────╯</b>\n"

    if user_rank == 0:
        text += (
            "\n<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            f"<b>Ты не входишь в топ по количеству выпитого кофе. Воспользуйся командой «пить кофе»</b>"
        )

    if user_rank > len(top_users) and ghoul:
        text += (
            f"\n<tg-emoji emoji-id=\'5316727448644103237\'>👤</tg-emoji> "
            f"Ты на <b>{user_rank}-м</b> месте — <b>выпито кофе:</b> <code>{format_num(ghoul.coffee_count)}</code>"
        )

    return text