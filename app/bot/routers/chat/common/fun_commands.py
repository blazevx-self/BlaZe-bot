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
        "Эта команда работает только в группе."
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
            f"Я выбираю {_name(member)}"
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
            "Дай хотя бы два варианта: <i>бот выбери пицца или суши</i>"
        )
        return

    await message.reply(
        "<tg-emoji emoji-id=\"5834766346390344283\">👉</tg-emoji> "
        f"Я выбираю: <b>{escape(truncate_text(choice, MAX_TEXT_LENGTH))}</b>"
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
        question = _text(match, "question")
        await message.reply(
            "<tg-emoji emoji-id=\"5834766346390344283\">👉</tg-emoji> "
            f"{question[:1].upper()}{question[1:]} — {_name(member)}"
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
        await message.reply("Для пары нужно хотя бы два участника.")
        return

    await message.reply(
        "<tg-emoji emoji-id=\"5834956020736069888\">💞</tg-emoji> "
        f"Пара: {_name(pair[0])} + {_name(pair[1])}"
    )

@router.message(F.text.regexp(TOP_PATTERN).as_("match"))
@inject
async def top(
    message: Message,
    match: re.Match[str],
    fun_service: FunService = Provide[Container.fun_command_service]
):
    if not await _only_group(message):
        return

    members = await fun_service.random_members(message.chat.id, TOP_SIZE)

    if not members:
        return

    lines = "\n".join(f"{i}. {_name(member)}" for i, member in enumerate(members, start=1))
    await message.reply(
        "<tg-emoji emoji-id=\"5386372946098939555\">🏆</tg-emoji> "
        f"Топ {_text(match, 'title')}:\n{lines}"
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
        f"Вероятность, что {_text(match, 'question')} — <b>{percent}%</b>"
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
        f"<b>{name}</b> {_text(match, 'quality')} на <b>{percent}%</b>"
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
        f"Оцениваю «{_text(match, 'subject')}» на <b>{score}/10</b>"
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
        f"Сколько {_text(match, 'question')} — <b>{value}</b>"
    )

@router.message(F.text.regexp(WHEN_PATTERN).as_("match"))
@inject
async def when(
    message: Message,
    match: re.Match[str],
    fun_command_service: FunService = Provide[Container.fun_command_service]
):
    day = fun_command_service.when(message.chat.id, match.group("question"))
    await message.reply(
        "<tg-emoji emoji-id=\"5891100675042974129\">📅</tg-emoji> "
        f"Когда {_text(match, 'question')} — <b>{day:%d.%m.%Y}</b>"
    )

@router.message(F.text.regexp(NUMBER_PATTERN).as_("match"))
async def number(message: Message, match: re.Match[str]):
    low, high = sorted((int(match.group("low")), int(match.group("high"))))
    await message.reply(f"🎲 <b>{random.randint(low, high)}</b>")

@router.message(F.text.regexp(COIN_PATTERN))
async def coin(message: Message):
    await message.reply(
        "<tg-emoji emoji-id=\"5778613750688911681\">🪙</tg-emoji> "
        f"<b>{random.choice(('Орёл', 'Решка'))}</b>"
    )

@router.message(F.text.regexp(DICE_PATTERN))
async def dice(message: Message):
    await message.answer_dice()