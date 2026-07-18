from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.configs.yaml import cfg

def get_help_menu():
    builder = InlineKeyboardBuilder()

    builder.button(text="📖 Лор проекта", url=cfg["settings"]["telegraph_link"])
    builder.button(text="📢 Канал автора", url=cfg["settings"]["channel_link"], icon_custom_emoji_id="6039381989985882045")
    builder.adjust(1)

    return builder.as_markup()


def get_help_menu_back():
    builder = InlineKeyboardBuilder()

    builder.button(text="📖 Лор проекта", url=cfg["settings"]["telegraph_link"])
    builder.button(text="📢 Канал автора", url=cfg["settings"]["channel_link"], icon_custom_emoji_id="6039381989985882045")
    builder.button(text="Назад", callback_data="back", icon_custom_emoji_id="5258132936401624790")

    builder.adjust(1)

    return builder.as_markup()

def get_help_menu_unknown_command():
    builder = InlineKeyboardBuilder()

    builder.button(text="📖 Лор проекта", url=cfg["settings"]["telegraph_link"])

    builder.adjust(1)

    return builder.as_markup()

