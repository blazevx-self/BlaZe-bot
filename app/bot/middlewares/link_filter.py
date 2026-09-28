import asyncio
from html import escape
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ChatPermissions, Message

from cachetools import TTLCache
from dependency_injector.wiring import Provide

from app.containers import Container
from app.core.constants.chat.chat_restrictions import MODERATOR_STATUSES
from app.core.constants.chat.link_filter import (
    LINK_ENTITY_TYPES,
    MIN_MESSAGES_FOR_LINKS,
    LINK_STRIKES_TTL,
    LINK_MUTE_DURATION,
    NOTICE_TTL_SECONDS,
    DANGEROUS_LINK_PATTERNS,
)

from app.database.repositories.chat.chat_member import ChatMemberRepository

from app.utils.logger import chat_logger
from app.utils.truncate_text import truncate_text

class LinkFilterMiddleware(BaseMiddleware):
    """Защита от ссылочного спама.

       Непроверенные участники: 1-я ссылка — предупреждение, 2-я — мут, 3-я — кик.
       Опасная ссылка (от любого, кроме админов) — сразу мут, повторно — кик.
    """

    def __init__(self) -> None:
        self._strikes: TTLCache = TTLCache(maxsize=10_000, ttl=LINK_STRIKES_TTL.total_seconds())
        self._tasks: set[asyncio.Task] = set()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
        chat_member_repo: ChatMemberRepository = Provide[Container.chat_member_repo],
    ) -> Any:
        if (
            event.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP)
            or not event.from_user
            or event.from_user.is_bot
            or event.sender_chat
        ):
            return await handler(event, data)


        links = self._extract_links(event)

        if not links:
            return await handler(event, data)

        member = await event.bot.get_chat_member(event.chat.id, event.from_user.id)

        if member.status in MODERATOR_STATUSES:
            return await handler(event, data)

        dangerous = self._is_dangerous(links)

        if not dangerous:
            db_member = await chat_member_repo.get_by_telegram_ids(
                event.chat.id,
                event.from_user.id
            )

            if db_member and db_member.messages_count >= MIN_MESSAGES_FOR_LINKS:
                return await handler(event, data)

        try:
            await event.delete()
        except TelegramAPIError:
            # нет права удалять - модерировать не можем, пропускаем
            return await handler(event, data)

        await self._punish(event, dangerous)

        return None

    @staticmethod
    def _extract_links(message: Message) -> list[tuple[str, str]]:
        """[(что видно на экране, куда реально ведёт)]"""

        text = message.text or message.caption or ""
        entities = message.entities or message.caption_entities or []
        links = []

        for entity in entities:
            if entity.type not in LINK_ENTITY_TYPES:
                continue

            visible = entity.extract_from(text)
            url = entity.url if entity.type == "text_link" else visible
            links.append((visible, url))

        return links

    @staticmethod
    def _is_dangerous(links: list[tuple[str, str]]) -> bool:
        for visible, url in links:
            url_lower = url.lower()
            visible_lower = visible.lower().rstrip("/")

            if any(pattern in url_lower for pattern in DANGEROUS_LINK_PATTERNS):
                return True

            # на экране одна ссылка, а ведёт на другую - фишинг
            looks_like_link = "http" in visible_lower or "t.me" in visible_lower

            if looks_like_link and visible_lower not in url_lower:
                return True

        return False

    async def _punish(self, message: Message, dangerous: bool) -> None:
        chat_id = message.chat.id
        user_id = message.from_user.id
        key = (chat_id, user_id)
        name = escape(truncate_text(message.from_user.first_name))

        strikes = self._strikes.get(key, 0) + 1

        if dangerous:
            strikes = max(strikes, 2)

        reason = "опасную ссылку" if dangerous else "спам ссылками"

        try:
            if strikes == 1:
                self._strikes[key] = strikes

                notice = await message.answer(
                    "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                    f"<b>{name}</b>, ссылки доступны после {MIN_MESSAGES_FOR_LINKS} сообщений в чате.\n"
                    "<b>Следующая ссылка — мут на 10 часов.</b>"
                )

                self._delete_later(notice)

            elif strikes == 2:
                self._strikes[key] = strikes

                await message.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=LINK_MUTE_DURATION
                )

                await message.answer(
                    "<tg-emoji emoji-id=\"5258267368877989660\">🔇</tg-emoji> "
                    f"<b>{name}</b> замучен на 10 часов за {reason}.\n"
                    "<i>Повторное нарушение — исключение из чата.</i>"
                )

            else:
                self._strikes.pop(key, None)

                await message.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
                await message.bot.unban_chat_member(chat_id=chat_id, user_id=user_id, only_if_banned=True)

                await message.answer(
                    "<tg-emoji emoji-id=\"6030329749409108167\">💬</tg-emoji>"
                    f"<b>{name}</b> исключён из чата за {reason}."
                )

        except TelegramAPIError as e:
            chat_logger.warning(
                f"[LINK_FILTER] Punish failed | chat_id={chat_id} | user_id={user_id} | "
                f"strikes={strikes} | {e}"
            )
            return

        chat_logger.info(
            f"[LINK_FILTER] Link removed | chat_id={chat_id} | user_id={user_id} | "
            f"strikes={strikes} | dangerous={dangerous}"
        )

    def _delete_later(self, message: Message) -> None:
        async def _delete() -> None:
            await asyncio.sleep(NOTICE_TTL_SECONDS)

            try:
                await message.delete()
            except TelegramAPIError:
                pass

        task = asyncio.create_task(_delete())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)