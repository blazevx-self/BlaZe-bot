from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_profile_to_ras_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Распрофиль', callback_data='open_ras_profile')]
    ])


def get_ras_to_profile_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Профиль', callback_data='open_profile')]
    ])