from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.config import cfg
from app.core.enums.quiz_status import QuizStatus

from app.services.game.quiz_service import quiz_service
from app.bot.keyboards.game.quiz_keyboard import get_quiz_again_kb

from app.bot.ui.quiz_ui import send_question_ui
from app.utils.logger import bot_logger

router = Router()

@router.message(Command("quiz"))
async def quiz(message: Message, user: dict):
    bot_logger.info(
        f"[COMMAND] name=\"{message.from_user.first_name}\" | user_id={message.from_user.id} | "
        f"chat={message.chat.type} | command=\"/quiz\""
    )
    result = await quiz_service.process_quiz_start(user=user)

    if result['status'] == QuizStatus.LIMIT:
        await message.reply(cfg['message']['quiz']['quiz_limit'])
        return

    if result['status'] == QuizStatus.NO_QUESTIONS:
        await message.reply(cfg['message']['quiz']['no_questions'], parse_mode="HTML")
        return

    await send_question_ui(message_or_call=message, q=result['question'], left=result['left'])

@router.callback_query(F.data.startswith(f"q_"))
async def quiz_handler(callback: CallbackQuery, user: dict):
    data = callback.data.split("_")
    question_id = int(data[1])
    user_choice = "_".join(data[2:])

    result = await quiz_service.process_quiz_answer(
        user=user,
        question_id=question_id,
        user_choice=user_choice
    )

    if result['status'] == QuizStatus.LIMIT:
        text = cfg['message']['quiz']['quiz_naebalovo_user']

        await callback.answer(text=text, show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=None)

        return

    if result['status'] == QuizStatus.LIMIT_REACHED:
        await callback.message.edit_text(text=result['text'], parse_mode='HTML', reply_markup=get_quiz_again_kb())
        await callback.answer()

        return

    await callback.message.edit_text(text=result['text'], parse_mode="HTML", reply_markup=get_quiz_again_kb())
    await callback.answer()

@router.callback_query(F.data == "quiz_again")
async def quiz_again(callback: CallbackQuery, user: dict):
    result = await quiz_service.process_quiz_start(user=user)

    if result['status'] == QuizStatus.LIMIT:
        await callback.answer(cfg['message']['quiz']['quiz_limit'], show_alert=True)
        return

    if result['status'] == QuizStatus.NO_QUESTIONS:
        await callback.answer(cfg['message']['quiz']['no_questions_callback'], show_alert=False)
        return

    await send_question_ui(message_or_call=callback, q=result['question'], left=result['left'])
    await callback.answer()