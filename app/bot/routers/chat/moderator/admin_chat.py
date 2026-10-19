from aiogram import Router, F
from aiogram.enums import ChatMemberStatus
from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.chat import ChatError

from app.services.chat.chat import ChatService
from app.bot.filters.group_only import GroupOnlyFilter, GroupModeratorFilter

router = Router()

BIND_PREFIX = "привязать чат"
UNBIND_PREFIX = "отвязать чат"
MODERATOR = {ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR}

def _parse_main_id(text: str, prefix: str) -> int | None:
    raw = text[len(prefix):].strip()

    try:
        return int(raw)
    except ValueError:
        return None

@router.message(
    F.text.lower().startswith(BIND_PREFIX),
    GroupOnlyFilter(),
    GroupModeratorFilter(),
)
@inject
async def bind_admin_chat(
    message: Message,
    chat_service: ChatService = Provide[Container.chat_service]
) -> None:
    if not message.text or not message.from_user:
        return

    main_id = _parse_main_id(message.text.lower(), BIND_PREFIX)

    if main_id is None:
        await message.reply(
            "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> "
            "<b>Не указан чат.</b>\n\n"
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            "<i>Пиши это в админ-группе.</i>\n\n"
            "<b>Пример:</b>\n"
            "<code>привязать чат -1001234567890</code>"
        )
        return

    # эту же группу нельзя назначить админкой самой себе
    if main_id == message.chat.id:
        await message.reply(
            "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
            "Нельзя привязать чат к самому себе."
        )
        return

    try:
        # бот должен состоять в ОСНОВНОМ чате, иначе get_chat падает
        main_chat = await message.bot.get_chat(main_id)
        member = await message.bot.get_chat_member(main_id, message.from_user.id)
    except TelegramAPIError:
        await message.reply(
            "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
            "Бота нет в этом чате или чат не найден."
        )
        return

    # кто вяжет - админ ОСНОВНОГО, не только админ-группы
    if member.status not in MODERATOR:
        await message.reply(
            "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
            "Ты не администратор основного чата."
        )
        return

    try:
        await chat_service.bind_admin_chat(
            main_telegram_id=main_id,
            admin_chat_id=message.chat.id
        )
    except ChatError as e:
        await message.reply(str(e))
        return

    await message.reply(
        "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
        f"<b>Этот чат привязан как админ-чат для</b> {main_chat.title}."
    )

@router.message(
    F.text.lower().startswith(UNBIND_PREFIX),
    GroupOnlyFilter(),
    GroupModeratorFilter(),
)
@inject
async def unbind_admin_chat(
    message: Message,
    chat_service: ChatService = Provide[Container.chat_service]
) -> None:
    if not message.text:
        return

    main_id = _parse_main_id(message.text.lower(), UNBIND_PREFIX)

    if main_id is None:
        await message.reply(
            "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> "
            "<b>Не указан чат.</b>\n\n"
            "<b>Пример:</b>\n"
            "<code>отвязать чат -1001234567890</code>"
        )
        return

    try:
        await chat_service.unbind_admin_chat(main_telegram_id=main_id)
    except ChatError as e:
        await message.reply(str(e))
        return

    await message.reply(
        "<tg-emoji emoji-id=\"5258130763148172425\">🗑</tg-emoji> "
        "Админ-чат отвязан."
    )