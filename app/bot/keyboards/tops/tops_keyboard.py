from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_balance_in_top_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Топ богатых", callback_data="money_top")]
    ])

def get_top_money_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить топчик", callback_data="update_only_top_money", icon_custom_emoji_id="5260687119092817530")],
        [InlineKeyboardButton(text="Мой баланс", callback_data="back_balance", icon_custom_emoji_id="5258391025281408576")]
    ])

def get_back_to_top_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_top", icon_custom_emoji_id="5258132936401624790")]
    ])

def get_balance_top_money_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить топчик", callback_data="update_top_money", icon_custom_emoji_id="5260687119092817530")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_balance", icon_custom_emoji_id="5258132936401624790")]
    ])

def get_update_top_clicks_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить топчик", callback_data="update_top_click", icon_custom_emoji_id="5260687119092817530")]
    ])

def get_update_top_kagune_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить топчик", callback_data="update_top_kagune", icon_custom_emoji_id="5260687119092817530")]
    ])