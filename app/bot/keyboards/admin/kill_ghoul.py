from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_kill_confirm_kb(target_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Убить",
        callback_data=f"kill_confirm_{target_id}",
        icon_custom_emoji_id="5294342418399783851",
    )
    builder.button(
        text="Отмена",
        callback_data="kill_cancel",
        icon_custom_emoji_id="5260342697075416641",
    )
    builder.adjust(1)
    return builder.as_markup()