from html import escape

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.configs.yaml import cfg
from app.core.enums import ResultStatus

from app.types.entities import UserData

from app.services.game.quiz_service import quiz_service
from app.bot.filters.owner_filter import OwnerCallbackFilter

from app.bot.keyboards.game.quiz_keyboard import get_quiz_again_kb
from app.bot.keyboards.game.quiz_keyboard import get_quiz_keyboard

from app.utils.logger import bot_logger


async def _send_question_ui(message_or_call, q, left, user_id):
    markup = get_quiz_keyboard(options_str=q['options'], question_id=q['id'], user_id=user_id)
    text = f"{escape(q['question'])}\n\n<i>осталось вопросов: {left}</i>"

    if isinstance(message_or_call, CallbackQuery):
        await message_or_call.message.edit_text(text=text, reply_markup=markup)
    else:
        await message_or_call.reply(text=text, reply_markup=markup)


router = Router()

@router.message(Command("quiz"))
@router.message(F.text.lower() == "викторина")
async def quiz(message: Message, user: UserData):
    result = await quiz_service.process_quiz_start(user=user)

    if result.status == ResultStatus.LIMIT:
        await message.reply(cfg['message']['quiz']['quiz_limit'])
        return

    if result.status == ResultStatus.NO_QUESTIONS:
        await message.reply(cfg['message']['quiz']['no_questions'])
        return

    await _send_question_ui(
        message_or_call=message,
        q=result.question,
        left=result.left,
        user_id=user.user_id
    )


@router.callback_query(F.data.startswith(f"q_"), OwnerCallbackFilter())
async def quiz_handler(callback: CallbackQuery, user: UserData):
    data = callback.data.split("_")

    question_id = int(data[1])
    user_choice = "_".join(data[2:-1])

    result = await quiz_service.process_quiz_answer(
        user=user,
        question_id=question_id,
        user_choice=user_choice
    )

    if result.status == ResultStatus.LIMIT:
        text = cfg['message']['quiz']['quiz_naebalovo_user']

        await callback.answer(text=text, show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=None)

        return

    if result.status == ResultStatus.LIMIT_REACHED:
        await callback.message.edit_text(text=result.text, reply_markup=get_quiz_again_kb(user.user_id))
        await callback.answer()

        return

    await callback.message.edit_text(text=result.text, reply_markup=get_quiz_again_kb(user.user_id))
    await callback.answer()


@router.callback_query(F.data.startswith("quiz_again_"), OwnerCallbackFilter())
async def quiz_again(callback: CallbackQuery, user: UserData):    
    result = await quiz_service.process_quiz_start(user=user)

    if result.status == ResultStatus.LIMIT:
        await callback.answer(cfg['message']['quiz']['quiz_limit'], show_alert=True)
        return

    if result.status == ResultStatus.NO_QUESTIONS:
        await callback.answer(cfg['message']['quiz']['no_questions_callback'], show_alert=False)
        return

    await _send_question_ui(
        message_or_call=callback,
        q=result.question,
        left=result.left,
        user_id=user.user_id
    )
    await callback.answer()