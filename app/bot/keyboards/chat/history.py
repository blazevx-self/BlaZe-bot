from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_history_kb(*, user_id: int, offset: int, has_next: bool, limit: int):
    builder = InlineKeyboardBuilder()

    if offset > 0:
        prev_offset = max(offset - limit, 0)
        builder.button(text="‹", callback_data=f"hist_{user_id}_{prev_offset}")

    if has_next:
        builder.button(text="›", callback_data=f"hist_{user_id}_{offset + limit}")

    builder.adjust(2)

    return builder.as_markup() if builder.buttons else None