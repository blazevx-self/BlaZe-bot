from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_reset_confirm_kb(action: str, target_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Удалить",
        callback_data=f"reset_{action}_confirm_{target_id}",
        icon_custom_emoji_id="5260416304224936047"
    )

    builder.button(
        text="Отменить",
        callback_data="reset_cancel",
        icon_custom_emoji_id="5260342697075416641"
    )

    builder.adjust(1)

    return builder.as_markup()