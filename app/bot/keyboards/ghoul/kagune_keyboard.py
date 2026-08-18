from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.utils.format_num import format_num
from app.configs.game import game_cfg

def get_open_kagune_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Пробудить кагуне', callback_data=f"kagune_new_{user_id}")]
    ])

def get_grow_kagune_kb(user_id: int) -> InlineKeyboardMarkup:
    price = game_cfg.kagune.start_price

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Растить кагуне ({format_num(price)} 💸)", callback_data=f"kagune_ras_{user_id}")]
    ])