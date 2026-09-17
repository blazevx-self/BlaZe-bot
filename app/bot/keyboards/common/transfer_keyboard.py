from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_transfer_confirm_kb(
    sender_id: int,
    receiver_id: int,
    amount: int
):
    builder = InlineKeyboardBuilder()

    builder.button(
        text='Подтвердить',
        callback_data=f"transfer_confirm_{receiver_id}_{amount}_{sender_id}",
        icon_custom_emoji_id="5260416304224936047"
    )

    builder.button(
        text="Отменить",
        callback_data=f"transfer_cancel_{sender_id}",
        icon_custom_emoji_id="5260342697075416641"
    )

    builder.adjust(1)

    return builder.as_markup()