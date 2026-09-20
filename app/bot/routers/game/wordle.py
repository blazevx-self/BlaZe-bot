import html

from aiogram import Router, Bot, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.constants.game.wordle import MAX_ATTEMPTS, WORD_LENGTH, MAX_LEN

from app.types.entities.user import UserData

from app.services.game.wordle.wordle_service import WordleService
from app.services.wikipedia_service import WikipediaService
from app.database.repositories import UserRepository

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
            f"<tg-emoji emoji-id=\"6041731551845159060\">🎉</tg-emoji> <b>ПОБЕДА!</b>\n\n"
            f"<tg-emoji emoji-id=\"5386795016830083674\">🎯</tg-emoji> Слово <b>{result.target_word}</b> угадано "
            f"за <b>{result.attempts_used}</b> {_attempts_word(result.attempts_used)}!\n\n"
            f"<tg-emoji emoji-id=\"5864068125112144897\">💸</tg-emoji> <code>+{result.earned}</code> на балик\n\n"
            "<tg-emoji emoji-id=\"5260687119092817530\">🔄</tg-emoji> Сыграть ещё <b> -> </b> /wordle"
        )

    if result.is_game_over:
        return (
            f"<tg-emoji emoji-id=\"5458779239941681169\">😔</tg-emoji> <b>Не повезло...</b>\n\n"
            f"<tg-emoji emoji-id=\"5386795016830083674\">🎯</tg-emoji> Загаданное слово: <b>{result.target_word}</b>\n\n"
            "<tg-emoji emoji-id=\"5260687119092817530\">🔄</tg-emoji> Попробовать снова <b> -> </b> /wordle"
        )

    return (
        f"{result.guess.to_emoji()}\n"
        f"Слово <b>{word.upper()}</b> — не то.\n"
        f"Попытка <code>{result.attempts_used}</code> из <code>{MAX_ATTEMPTS}</code>, "
        f"осталось <code>{result.attempts_left}</code>"
    )

async def _word_info_block(wikipedia_service: WikipediaService, word: str) -> str:
    result = await wikipedia_service.get_description(word)

    if not result or not getattr(result, "text", ""):
        return ""

    text = result.text.strip()

    if "может означать:" in text.lower() or "многозначный термин" in text.lower():
        # Разделяем часть после двоеточия со списком значений
        _, _, values_part = text.partition(":")
        # Разбиваем на строки, убираем пустые, берем первые 3 примера
        variants = [v.strip().strip("—- ").strip() for v in values_part.split("\n") if v.strip()][:3]
        if variants:
            variants_text = "\n".join(f"▫️ {html.escape(v)}" for v in variants)
            return (
                f"\n\n<tg-emoji emoji-id=\"5258328383183396223\">📖</tg-emoji> "
                f"<b>{html.escape(word.upper())}</b> — многозначный термин, основные значения:\n\n"
                f"<i>{variants_text}</i>"
            )

    if len(text) > MAX_LEN:
        cut = text[:MAX_LEN]

        for sep in (". ", "! ", "? ", "\n"):
            if sep in cut:
                cut = cut.rsplit(sep, 1)[0] + "."
                break
        cleaned = cut.rstrip() + ("..." if not cut.endswith((".", "!", "?")) else "")
    else:
        cleaned = text

    return (
        f"\n\n<tg-emoji emoji-id=\"5258328383183396223\">📖</tg-emoji> "
        f"<b>{html.escape(word.upper())}:</b>\n\n"
        f"<i>{html.escape(cleaned)}</i>"
    )

async def _delete_board(bot: Bot, chat_id: int, message_id: int) -> bool:
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        return True

    except TelegramBadRequest:
        return False

@router.message(Command("wordle"))
@router.message(F.text.lower() == "вротли")
@inject
async def wordle_start(
    message: Message,
    bot: Bot,
    wordle_service: WordleService = Provide[Container.wordle_service]
):
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
            caption=(
                "<tg-emoji emoji-id=\"5891211339170326418\">⏳</tg-emoji> "
                "<b>У вас есть незавершённая игра.</b>\n\n<i>Введите слово из 5 букв чтобы продолжить.</i>"
            )
        )
        wordle_service.set_board_message_id(user_id, sent.message_id)
        return

    photo = wordle_service.start_game(telegram_id=user_id)
    
    sent = await message.reply_photo(
        photo=BufferedInputFile(file=photo, filename="wordle.png"),
        caption=(
            "<tg-emoji emoji-id=\"5884089033558070257\">⬜️</tg-emoji> "
            "<b>Новая игра Wordle!</b>\n\n"
            f"<i>Угадайте слово из {WORD_LENGTH} букв за {MAX_ATTEMPTS} попыток.</i>\n\n"
            "🟩 — буква на своём месте\n"
            "🟨 — буква есть, но не там\n"
            "⬛ — буквы нет в слове"
        )
    )

    wordle_service.set_board_message_id(user_id, sent.message_id)

@router.message(WordleGameFilter())
@inject
async def wordle_guess(
    message: Message,
    bot: Bot,
    user: UserData,
    user_repo: UserRepository = Provide[Container.user_repo],
    wordle_service: WordleService = Provide[Container.wordle_service],
    wikipedia_service: WikipediaService = Provide[Container.wikipedia_service]
):
    if not message.from_user or not message.text:
        return

    user_id = message.from_user.id
    word = message.text.strip()

    old_message_id = wordle_service.get_board_message_id(user_id)

    try:
        result = await wordle_service.make_guess(
            telegram_id=user_id,
            word=word,
            user=user,
            user_repo=user_repo,
        )
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

    if result.is_win or result.is_game_over:
        word_info = await _word_info_block(wikipedia_service, result.target_word)
        if word_info:
            await sent.reply(
                text=word_info,
                disable_web_page_preview=True
            )