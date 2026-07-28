from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.configs.yaml import cfg
from app.core.enums import ResultStatus
from app.types.entities import UserData

from app.services.game.quiz_service import quiz_service

from app.bot.keyboards.game.quiz_keyboard import get_quiz_again_kb
from app.bot.ui.quiz_ui import send_question_ui

from app.utils.logger import bot_logger


router = Router()

@router.message(Command("quiz"))
async def quiz(message: Message, user: UserData):
    bot_logger.info(
        f"[COMMAND] name=\"{message.from_user.first_name}\" | user_id={message.from_user.id} | "
        f"chat={message.chat.type} | command=\"/quiz\""
    )

    result = await quiz_service.process_quiz_start(user=user)

    if result.status == ResultStatus.LIMIT:
        await message.reply(cfg['message']['quiz']['quiz_limit'])
        return

    if result.status == ResultStatus.NO_QUESTIONS:
        await message.reply(cfg['message']['quiz']['no_questions'])
        return

    await send_question_ui(
        message_or_call=message,
        q=result.question,
        left=result.left,
        user_id=user.user_id
    )


@router.callback_query(F.data.startswith(f"q_"))
async def quiz_handler(callback: CallbackQuery, user: UserData):
    data = callback.data.split("_")

    question_id = int(data[1])
    owner_id = int(data[2])
    user_choice = "_".join(data[3:])

    if callback.from_user.id != owner_id:
        await callback.answer(
            text="☕️ Это не твоя викторина, не мешай людям отвечать на вопросы.\n\n"
            "Сам викторину свою вызывай -> /quiz и проходи", show_alert=True
        )

        return

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

    user.money = result.new_money

    if result.status == ResultStatus.LIMIT_REACHED:
        await callback.message.edit_text(text=result.text, reply_markup=get_quiz_again_kb())
        await callback.answer()

        return

    await callback.message.edit_text(text=result.text, reply_markup=get_quiz_again_kb())
    await callback.answer()


@router.callback_query(F.data == "quiz_again")
async def quiz_again(callback: CallbackQuery, user: UserData):
    result = await quiz_service.process_quiz_start(user=user)

    if result.status == ResultStatus.LIMIT:
        await callback.answer(cfg['message']['quiz']['quiz_limit'], show_alert=True)
        return

    if result.status == ResultStatus.NO_QUESTIONS:
        await callback.answer(cfg['message']['quiz']['no_questions_callback'], show_alert=False)
        return

    await send_question_ui(
        message_or_call=callback,
        q=result.question,
        left=result.left,
        user_id=user.user_id
    )
    await callback.answer()