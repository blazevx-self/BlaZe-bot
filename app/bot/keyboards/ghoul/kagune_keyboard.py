from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.utils.format_num import format_num
from app.configs.game import game_cfg

def get_open_kagune_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Пробудить кагуне', callback_data='kagune_new')]
    ])

def get_grow_kagune_kb() -> InlineKeyboardMarkup:
    price = game_cfg.kagune.start_price

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Растить кагуне ({format_num(price)} 💸)", callback_data="kagune_ras")]
    ])