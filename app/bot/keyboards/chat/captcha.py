from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_captcha_kb(user_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Я человек",
        callback_data=f"captcha_{user_id}",
        icon_custom_emoji_id="5258093637450866522"
    )

    return builder.as_markup()