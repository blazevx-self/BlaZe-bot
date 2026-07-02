from aiogram.types import CallbackQuery
from app.bot.keyboards.game.quiz_keyboard import get_quiz_keyboard

async def send_question_ui(message_or_call, q, left):
    markup = get_quiz_keyboard(
        options_str=q['options'],
        question_id=q['id']
    )
    text = f"{q['question']}\n\n<i>осталось вопросов: {left}</i>"

    if isinstance(message_or_call, CallbackQuery):
        await message_or_call.message.edit_text(
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
    else:
        await message_or_call.reply(
            text=text,
            reply_markup=markup,
            parse_mode='HTML'
        )
