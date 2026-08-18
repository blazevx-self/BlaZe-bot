from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_balance_in_top_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Топ богатых", callback_data=f"money_top_{user_id}")]
    ])

def get_top_money_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить топчик", callback_data=f"update_only_top_money_{user_id}", icon_custom_emoji_id="5260687119092817530")],
        [InlineKeyboardButton(text="Мой баланс", callback_data=f"back_balance_{user_id}", icon_custom_emoji_id="5258391025281408576")]
    ])

def get_back_to_top_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data=f"back_to_top_{user_id}", icon_custom_emoji_id="5258132936401624790")]
    ])

def get_balance_top_money_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить топчик", callback_data=f"update_top_money_{user_id}", icon_custom_emoji_id="5260687119092817530")],
        [InlineKeyboardButton(text="Назад", callback_data=f"back_to_balance_{user_id}", icon_custom_emoji_id="5258132936401624790")]
    ])

def get_update_top_snap_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить топчик", callback_data="update_top_snap", icon_custom_emoji_id="5260687119092817530")]
    ])

def get_update_top_kagune_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить топчик", callback_data="update_top_kagune", icon_custom_emoji_id="5260687119092817530")]
    ])

def get_update_top_coffee_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить топчик", callback_data="update_top_coffee", icon_custom_emoji_id="5260687119092817530")]
    ])

    