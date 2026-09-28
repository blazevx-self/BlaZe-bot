import random
import re

from html import escape

from aiogram import Router, F
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.constants.chat.fun_command import (
    PICK_MEMBER_PATTERN,
    PICK_PATTERN,
    WHO_PATTERN,
    CHANCE_PATTERN,
    HOW_MUCH_PATTERN,
    RATE_PATTERN,
    WHEN_PATTERN,
    COUNT_PATTERN,
    NUMBER_PATTERN,
    COUPLE_PATTERN,
    TOP_PATTERN,
    COIN_PATTERN,
    DICE_PATTERN,
    MAX_TEXT_LENGTH,
    TOP_SIZE,
)

from app.types.entities.user import UserData
from app.services.chat.common.fun_commands import FunService

from app.utils.truncate_text import truncate_text

router = Router()

GROUP_TYPES = ("group", "supergroup")

def _name(user: UserData) -> str:
    return f"<b>{escape(truncate_text(user.name))}</b>"

def _text(match: re.Match[str], group: str) -> str:
    return escape(truncate_text(match.group(group).strip(), MAX_TEXT_LENGTH))

async def _only_group(message: Message) -> bool:
    if message.chat.type in GROUP_TYPES:
        return True

    await message.reply(
        "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
        + FunService.phrase("only_group", "Эта команда работает только в группе.")
    )
    return False

# порядок важен: «выбери участника» выше «выбери A или B»

@router.message(F.text.regexp(PICK_MEMBER_PATTERN))
@inject
async def pick_member(
    message: Message,
    fun_command_service: FunService = Provide[Container.fun_command_service]
):
    if not await _only_group(message):
        return

    member = await fun_command_service.random_member(message.chat.id)

    if member:
        await message.reply(
            "<tg-emoji emoji-id=\"5834766346390344283\">👉</tg-emoji> "
            + fun_command_service.phrase("pick_member", "Я выбираю {name}", name=_name(member))
        )

@router.message(F.text.regexp(PICK_PATTERN).as_("match"))
@inject
async def pick_option(
    message: Message,
    match: re.Match[str],
    fun_command_service: FunService = Provide[Container.fun_command_service]
):
    choice = fun_command_service.pick_option(match.group("options"))

    if not choice:
        await message.reply(
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            + fun_command_service.phrase("pick_too_few", "Дай хотя бы два варианта: <i>бот выбери пицца или суши</i>")
        )
        return

    await message.reply(
        "<tg-emoji emoji-id=\"5834766346390344283\">👉</tg-emoji> "
        + fun_command_service.phrase(
            "pick", "Я выбираю: {choice}",
            choice=f"<b>{escape(truncate_text(choice, MAX_TEXT_LENGTH))}</b>",
        )
    )

@router.message(F.text.regexp(WHO_PATTERN).as_("match"))
@inject
async def who(
    message: Message,
    match: re.Match[str],
    fun_command_service: FunService = Provide[Container.fun_command_service]
):
    if not await _only_group(message):
        return

    member = await fun_command_service.random_member(message.chat.id)

    if member:
        text = fun_command_service.phrase(
            "who", "{question} — {name}",
            question=_text(match, "question"), name=_name(member),
        )

        await message.reply(
            "<tg-emoji emoji-id=\"5834766346390344283\">👉</tg-emoji> "
            f"{text[:1].upper()}{text[1:]}"
        )

@router.message(F.text.regexp(COUPLE_PATTERN))
@inject
async def couple(
    message: Message,
    fun_command_service: FunService = Provide[Container.fun_command_service]
):
    if not await _only_group(message):
        return

    pair = await fun_command_service.random_members(message.chat.id, 2)

    if len(pair) < 2:
        await message.reply(
            fun_command_service.phrase(
                "couple_too_few", "Для пары нужно хотя бы два участника.")
        )
        return

    await message.reply(
        "<tg-emoji emoji-id=\"5834956020736069888\">💞</tg-emoji> "
        + fun_command_service.phrase(
            "couple", "Пара: {first} + {second}",
            first=_name(pair[0]), second=_name(pair[1]),
        )
    )

@router.message(F.text.regexp(TOP_PATTERN).as_("match"))
@inject
async def top(
    message: Message,
    match: re.Match[str],
    fun_command_service: FunService = Provide[Container.fun_command_service]
):
    if not await _only_group(message):
        return

    members = await fun_command_service.random_members(message.chat.id, TOP_SIZE)

    if not members:
        return

    lines = "\n".join(f"{i}. {_name(member)}" for i, member in enumerate(members, start=1))

    await message.reply(
        "<tg-emoji emoji-id=\"5386372946098939555\">🏆</tg-emoji> "
        + fun_command_service.phrase("top", "Топ {title}:\n{list}", title=_text(match, "title"), list=lines)
    )

@router.message(F.text.regexp(CHANCE_PATTERN).as_("match"))
@inject
async def chance(
    message: Message,
    match: re.Match[str],
    fun_command_service: FunService = Provide[Container.fun_command_service]
):
    percent = fun_command_service.chance(message.chat.id, match.group("question"))

    await message.reply(
        "<tg-emoji emoji-id=\"5936143551854285132\">📊</tg-emoji> "
        + fun_command_service.phrase(
            "chance", "Вероятность, что {question} — {percent}",
            question=_text(match, "question"), percent=f"<b>{percent}%</b>",
        )
    )

@router.message(F.text.regexp(HOW_MUCH_PATTERN).as_("match"))
@inject
async def how_much(
    message: Message,
    match: re.Match[str],
    fun_command_service: FunService = Provide[Container.fun_command_service]
):
    if not message.from_user:
        return

    percent = fun_command_service.how_much(message.chat.id, message.from_user.id, match.group("quality"))
    name = escape(truncate_text(message.from_user.first_name))

    await message.reply(
        "<tg-emoji emoji-id=\"5875012827063783367\">📈</tg-emoji> "
        + fun_command_service.phrase(
            "how_much", "{name} {quality} на {percent}",
            name=f"<b>{name}</b>", quality=_text(match, "quality"), percent=f"<b>{percent}%</b>",
        )
    )

@router.message(F.text.regexp(RATE_PATTERN).as_("match"))
@inject
async def rate(
    message: Message,
    match: re.Match[str],
    fun_command_service: FunService = Provide[Container.fun_command_service]
):
    score = fun_command_service.rate(message.chat.id, match.group("subject"))

    await message.reply(
        "<tg-emoji emoji-id=\"5874969477958864343\">⭐️</tg-emoji> "
        + fun_command_service.phrase(
            "rate", "Оцениваю «{subject}» на {score}",
            subject=_text(match, "subject"), score=f"<b>{score}/10</b>",
        )
    )

@router.message(F.text.regexp(COUNT_PATTERN).as_("match"))
@inject
async def count(
    message: Message,
    match: re.Match[str],
    fun_command_service: FunService = Provide[Container.fun_command_service]
):
    value = fun_command_service.count(message.chat.id, match.group("question"))

    await message.reply(
        "<tg-emoji emoji-id=\"5877341966353567513\">🔢</tg-emoji> "
        + fun_command_service.phrase(
            "count", "Сколько {question} — {value}",
            question=_text(match, "question"), value=f"<b>{value}</b>",
        )
    )

@router.message(F.text.regexp(WHEN_PATTERN).as_("match"))
@inject
async def when(
    message: Message,
    match: re.Match[str],
    fun_command_service: FunService = Provide[Container.fun_command_service]
):
    day = fun_command_service.when(message.chat.id, match.group("question"))

    text = fun_command_service.phrase(
        "when", "Когда {question} — {date}",
        question=_text(match, "question"), date=f"<b>{day:%d.%m.%Y}</b>",
    )

    await message.reply(
        "<tg-emoji emoji-id=\"5891100675042974129\">📅</tg-emoji> "
        f"{text[:1].upper()}{text[1:]}"
    )

@router.message(F.text.regexp(NUMBER_PATTERN).as_("match"))
async def number(message: Message, match: re.Match[str]):
    low, high = sorted((int(match.group("low")), int(match.group("high"))))
    await message.reply(f"🎲 <b>{random.randint(low, high)}</b>")

@router.message(F.text.regexp(COIN_PATTERN))
async def coin(message: Message):
    side = f"<b>{random.choice(('Орёл', 'Решка'))}</b>"

    await message.reply(
        "<tg-emoji emoji-id=\"5778613750688911681\">🪙</tg-emoji> "
        + FunService.phrase("coin", "{side}", side=side)
    )

@router.message(F.text.regexp(DICE_PATTERN))
async def dice(message: Message):
    await message.answer_dice()