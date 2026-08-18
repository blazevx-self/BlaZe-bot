import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_quiz_keyboard(options_str: str, question_id: int, user_id: int) -> InlineKeyboardMarkup:
    options = options_str.split('|')
    random.shuffle(options)

    keyboard = []
    row = []

    for opt in options:
        btn = InlineKeyboardButton(text=opt, callback_data=f"q_{question_id}_{opt}_{user_id}")
        row.append(btn)

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_quiz_again_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сыграть ещё раз', callback_data=f"quiz_again_{user_id}", icon_custom_emoji_id='5260450573768990626')]
    ])
