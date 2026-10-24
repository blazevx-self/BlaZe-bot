from aiogram.utils.keyboard import InlineKeyboardBuilder

def offer_kb(proposal_id: int, initiator_tg: int):
    b = InlineKeyboardBuilder()

    b.button(
        text="Сделать предложение",
        callback_data=f"fam_pay_{proposal_id}_{initiator_tg}",
        icon_custom_emoji_id="5402100905883488232",
    )

    return b.as_markup()

def proposal_kb(
    proposal_id: int,
    initiator_tg: int,
    target_tg: int,
    bot_username: str,
    *,
    initiator_ok: bool,
    target_ok: bool,
):
    b = InlineKeyboardBuilder()

    if not initiator_ok:
        b.button(
            text="Подтверждаю",
            callback_data=f"fam_ok_{proposal_id}_{initiator_tg}",
            icon_custom_emoji_id="5260416304224936047",
        )

    if not target_ok:
        b.button(
            text="Согласен(на)",
            callback_data=f"fam_ok_{proposal_id}_{target_tg}",
            icon_custom_emoji_id="5260416304224936047",
        )

    b.button(
        text="Отказаться",
        callback_data=f"fam_no_{proposal_id}",
        icon_custom_emoji_id="5260342697075416641",
    )

    b.button(
        text="Подтвердить в личке",
        url=f"https://t.me/{bot_username}?start=fam_{proposal_id}",
    )

    b.adjust(2, 1, 1)
    return b.as_markup()

def rename_kb(rename_id: int, other_tg: int, bot_username: str):
    b = InlineKeyboardBuilder()

    b.button(
        text="Согласен(на)",
        callback_data=f"fam_rn_ok_{rename_id}_{other_tg}",
        icon_custom_emoji_id="5260416304224936047",
    )

    b.button(
        text="Против",
        callback_data=f"fam_rn_no_{rename_id}_{other_tg}",
        icon_custom_emoji_id="5260342697075416641",
    )

    b.button(
        text="Ответить в личке",
        url=f"https://t.me/{bot_username}?start=famrn_{rename_id}",
    )

    b.adjust(2, 1)
    return b.as_markup()

def divorce_kb(user_tg: int):
    b = InlineKeyboardBuilder()

    b.button(
        text="Развестись",
        callback_data=f"fam_div_{user_tg}",
        icon_custom_emoji_id="5836847700426887322",
    )

    return b.as_markup()