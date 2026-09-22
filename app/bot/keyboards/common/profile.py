from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_profile_to_ras_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Распрофиль', callback_data=f'open_ras_profile_{user_id}')]
    ])

def get_ras_to_profile_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Профиль', callback_data=f'open_profile_{user_id}')]
    ])