from aiogram import Router, Bot, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from app.core.constants.game.wordle import MAX_ATTEMPTS, WORD_LENGTH
from app.types.entities.user import UserData

from app.services.game.wordle.wordle_service import WordleService
from app.bot.filters.wordle_filter import WordleGameFilter

router = Router()

def _attempts_word(number: int) -> str:
    """Склонение слово 'попытка'"""

    if 11 <= number % 100 <= 14:
        return "попыток"

    match number % 10:
        case 1:
            return "попытка"
        case 2 | 3 | 4:
            return "попытки"
        case _:
            return "попыток"


def _build_caption(result, word: str) -> str | None:
    if result.is_win:
        return (
            f"🎉 <b>ПОБЕДА!</b>\n\n"
            f"Слово <b>{result.target_word}</b> угадано "
            f"за <b>{result.attempts_used}</b> {_attempts_word(result.attempts_used)}!\n"
            f"💸 <code>+{result.earned}</code> на балик\n\n"
            "Сыграть ещё <b> -> </b> /wordle"
        )

    if result.is_game_over:
        return (
            f"😔 <b>Не повезло...</b>\n\n"
            f"Загаданное слово: <b>{result.target_word}</b>\n"
            "Попробовать снова <b> -> </b> /wordle"
        )

    return (
        f"{result.guess.to_emoji()}\n"
        f"Слово <b>{word.upper()}</b> — не то.\n"
        f"Попытка <code>{result.attempts_used}</code> из <code>{MAX_ATTEMPTS}</code>, "
        f"осталось <code>{result.attempts_left}</code>"
    )


async def _delete_board(bot: Bot, chat_id: int, message_id: int) -> bool:
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        return True

    except TelegramBadRequest:
        return False


@router.message(Command("wordle"))
@router.message(F.text.lower() == "вротли")
async def wordle_start(message: Message, bot: Bot, wordle_service: WordleService):
    if not message.from_user:
        return

    user_id = message.from_user.id
    photo = wordle_service.get_board(telegram_id=user_id)
    
    if photo:
        old_message_id = wordle_service.get_board_message_id(user_id)

        if old_message_id:
            await _delete_board(bot, message.chat.id, old_message_id)

        sent = await message.reply_photo(
            photo=BufferedInputFile(file=photo, filename="wordle.png"),
            caption="⏳ У вас есть незавершённая игра.\nВведите слово из 5 букв чтобы продолжить."
        )
        wordle_service.set_board_message_id(user_id, sent.message_id)
        return

    photo = wordle_service.start_game(telegram_id=user_id)
    
    sent = await message.reply_photo(
        photo=BufferedInputFile(file=photo, filename="wordle.png"),
        caption=(
            "🟩 <b>Новая игра Wordle!</b>\n\n"
            f"Угадайте слово из {WORD_LENGTH} букв за {MAX_ATTEMPTS} попыток.\n\n"
            "🟩 — буква на своём месте\n"
            "🟨 — буква есть, но не там\n"
            "⬛ — буквы нет в слове"
        )
    )
    wordle_service.set_board_message_id(user_id, sent.message_id)

@router.message(WordleGameFilter())
async def wordle_guess(
        message: Message,
        bot: Bot,
        user: UserData,
        wordle_service: WordleService
):
    if not message.from_user or not message.text:
        return

    user_id = message.from_user.id
    word = message.text.strip()

    old_message_id = wordle_service.get_board_message_id(user_id)

    try:
        result = await wordle_service.make_guess(telegram_id=user_id, word=word, user=user)
    except ValueError as e:
        await message.reply(str(e))
        return

    if not result:
        return

    caption = _build_caption(result, word)
    photo = BufferedInputFile(file=result.image, filename="wordle.png")
    
    if old_message_id:
        await _delete_board(bot, message.chat.id, old_message_id)

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    sent = await message.answer_photo(photo=photo, caption=caption)
    wordle_service.set_board_message_id(user_id, sent.message_id)