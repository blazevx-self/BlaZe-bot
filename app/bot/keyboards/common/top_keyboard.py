from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_ghoul_top_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Топ богатых", callback_data="top")]
    ])

def get_update_top_only_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить топчик", callback_data="update_top_only", icon_custom_emoji_id="5260687119092817530")],
        [InlineKeyboardButton(text="Мой баланс", callback_data="back_to_balance", icon_custom_emoji_id="5258391025281408576")]
    ])

def get_back_to_top_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_top", icon_custom_emoji_id="5258132936401624790")]
    ])

def get_top_ghoul_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить топчик", callback_data="update_top", icon_custom_emoji_id="5260687119092817530")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_ghoul", icon_custom_emoji_id="5258132936401624790")]
    ])