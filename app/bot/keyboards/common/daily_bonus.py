from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_bonus_keyboard(user_id: int, boxes: int) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=" ",
            callback_data=f"bonus_open_{user_id}",
            icon_custom_emoji_id="6032644646587338669"
        )
        for _ in range(boxes)
    ]

    return InlineKeyboardMarkup(inline_keyboard=[
        buttons[i:i + 2] for i in range(0, len(buttons), 2)
    ])