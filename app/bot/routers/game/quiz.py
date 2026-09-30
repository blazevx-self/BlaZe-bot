import json
from html import escape

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.configs.yaml_loader import cfg

from app.core.enums import ResultStatus
from app.types.entities.user import UserData

from app.services.game.quiz import QuizService
from app.bot.filters.owner import OwnerCallbackFilter

from app.bot.keyboards.game.quiz import get_quiz_again_kb
from app.bot.keyboards.game.quiz import get_quiz_keyboard

async def _safe_edit(message: Message, **kwargs) -> None:
    try:
        await message.edit_text(**kwargs)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

async def _send_question_ui(message_or_call, q, left, user_id):
    markup = get_quiz_keyboard(
        options_str=q.options,
        question_id=q.id,
        user_id=user_id
    )

    text = (
        "<tg-emoji emoji-id=\"6030848053177486888\">❓</tg-emoji> "
        f"{escape(q.question)}\n\n"
        "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
        f"<i>осталось вопросов: {left}</i>"
    )

    if isinstance(message_or_call, CallbackQuery):
        await _safe_edit(message_or_call.message, text=text, reply_markup=markup)
    else:
        await message_or_call.reply(text=text, reply_markup=markup)

router = Router()

@router.message(Command("quiz"))
@inject
async def quiz(
    message: Message,
    user: UserData,
    quiz_service: QuizService = Provide[Container.quiz_service]
):
    result = await quiz_service.quiz_start(user=user)

    if result.status == ResultStatus.LIMIT:
        await message.reply(cfg['message']['quiz']['quiz_limit']['message'])
        return

    if result.status == ResultStatus.NO_QUESTIONS:
        await message.reply(cfg['message']['quiz']['no_questions'])
        return

    await _send_question_ui(
        message_or_call=message,
        q=result.question,
        left=result.left,
        user_id=user.telegram_id
    )

@router.callback_query(F.data.startswith(f"q_"), OwnerCallbackFilter())
@inject
async def quiz_handler(
    callback: CallbackQuery,
    user: UserData,
    quiz_service: QuizService = Provide[Container.quiz_service]
):
    data = callback.data.split("_")

    question_id = int(data[1])
    option_index = int(data[2])

    question = await quiz_service.quiz_repo.get_question_by_id(question_id)

    options = json.loads(question.options)

    if not 0 <= option_index < len(options):
        await callback.answer("🔄 Вопрос изменился, начни заново.", show_alert=False)
        return

    user_choice = options[option_index]

    result = await quiz_service.quiz_answer(
        user=user,
        question_id=question_id,
        user_choice=user_choice
    )

    if result.status == ResultStatus.LIMIT:
        await callback.answer("💬 Лимит вопросов исчерпан.", show_alert=False)
        return

    if result.status == ResultStatus.LIMIT_REACHED:
        await callback.message.edit_text(text=result.text, reply_markup=get_quiz_again_kb(user.telegram_id))
        await callback.answer()

        return

    await _safe_edit(callback.message, text=result.text, reply_markup=get_quiz_again_kb(user.telegram_id))
    await callback.answer()

@router.callback_query(F.data.startswith("quiz_again_"), OwnerCallbackFilter())
@inject
async def quiz_again(
    callback: CallbackQuery,
    user: UserData,
    quiz_service: QuizService = Provide[Container.quiz_service]
):
    result = await quiz_service.quiz_start(user=user)

    if result.status == ResultStatus.LIMIT:
        await callback.answer(cfg['message']['quiz']['quiz_limit']['callback'], show_alert=True)
        return

    if result.status == ResultStatus.NO_QUESTIONS:
        await callback.answer(cfg['message']['quiz']['no_questions_callback'], show_alert=False)
        return

    await _send_question_ui(
        message_or_call=callback,
        q=result.question,
        left=result.left,
        user_id=user.telegram_id
    )
    await callback.answer()