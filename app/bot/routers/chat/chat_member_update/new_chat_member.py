from html import escape

from aiogram import Router, F
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatMemberUpdated, LinkPreviewOptions, Message, CallbackQuery, ChatJoinRequest
from aiogram.exceptions import TelegramAPIError
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    IS_MEMBER, IS_NOT_MEMBER,
)

from dependency_injector.wiring import inject, Provide

from app.bot.filters.owner import OwnerCallbackFilter
from app.containers import Container
from app.configs.game import game_cfg

from app.core.constants.chat.captcha import CAPTCHA_TIMEOUT
from app.core.exceptions.chat import CaptchaError

from app.database.repositories.chat.chat import ChatRepository

from app.services.chat.chat import ChatService
from app.services.chat.common.captcha import CaptchaService

from app.bot.keyboards.common.help import get_help_menu
from app.bot.keyboards.chat.captcha import get_captcha_kb

from app.utils.logger import bot_logger, error_logger

router = Router()

@router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
@inject
async def bot_added(
    event: ChatMemberUpdated,
    chat_repo: ChatRepository = Provide[Container.chat_repo]
) -> None:
    if event.chat.type not in ("group", "supergroup"):
        return

    already_known = (await chat_repo.get_chat_by_telegram_id(event.chat.id)) is not None

    await chat_repo.upsert(
        telegram_id=event.chat.id,
        title=event.chat.title,
        username=event.chat.username
    )

    if already_known:
        return

    bot_logger.info(
        f"[BOT] Added | title_chat=\"{event.chat.title}\" | chat_id={event.chat.id} | "
        f"chat_username={event.chat.username} | type={event.chat.type}"
    )

    try:
       await event.bot.send_message(
           chat_id=event.chat.id,
           text=(
               "<tg-emoji emoji-id=\"5289581576001167896\">🤨</tg-emoji> "
               "<b>Ебать, вы меня добавили? Ну пиздата конечно!</b>\n\n"
               "<i>Я — бот по вселенной Токийского Гуля.</i>\n\n"
               f"<i>Меня написал</i> <i>{escape(event.from_user.first_name)},</i> "
               "<i>так что если буду не так работать и тупить — пишите ему о том почему так произошло.</i>\n\n"
               "<tg-emoji emoji-id=\"5258461531464539536\">📌</tg-emoji> "
               "<b>Ознакомьтесь с лором и командами по ссылке и кнопкам ниже: </b>"
               f'<a href="{game_cfg.start.guide_link}">\u200b</a>'
           ),
           reply_markup=get_help_menu(),
           link_preview_options=LinkPreviewOptions(is_disabled=False)
       )

    except TelegramAPIError as e:
        error_logger.exception(
            f"[BOT] Welcome message failed | chat_id={event.chat.id} | "
            f"chat_username={event.chat.username} | error={e}"
        )

@router.message(F.migrate_to_chat_id)
@inject
async def chat_migrated(
    message: Message,
    chat_repo: ChatRepository = Provide[Container.chat_repo]
) -> None:
    await chat_repo.migrate(
        old_telegram_id=message.chat.id,
        new_telegram_id=message.migrate_to_chat_id
    )

    bot_logger.info(
        f"[BOT] Chat migrated | old_id={message.chat.id} | new_id={message.migrate_to_chat_id}"
    )

@router.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def bot_removed(event: ChatMemberUpdated) -> None:
    bot_logger.info(
        f"[BOT] Removed | title_chat=\"{event.chat.title}\" | "
        f"chat_id={event.chat.id} | chat_username={event.chat.username} | type={event.chat.type}"
    )

@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
@inject
async def member_joined(
    event: ChatMemberUpdated,
    chat_repo: ChatRepository = Provide[Container.chat_repo],
    chat_service: ChatService = Provide[Container.chat_service],
    captcha_service: CaptchaService = Provide[Container.captcha_service]
) -> None:
    if event.chat.type not in ("group", "supergroup"):
        return

    member = event.new_chat_member.user

    if member.is_bot:
        return

    if event.new_chat_member.status in (
        ChatMemberStatus.CREATOR,
        ChatMemberStatus.ADMINISTRATOR
    ):
        await _send_welcome(event, chat_service)
        return

    chat = await chat_repo.get_chat_by_telegram_id(event.chat.id)

    if chat and chat.captcha_enabled:
        text = (
            f"<tg-emoji emoji-id=\"6043960760130868895\">🤔</tg-emoji> "
            f"<b>{escape(member.first_name)}</b>, ты кто?\n\n"
            "<i>Нажми кнопку, пока не выкинул.</i>\n\n"
            f"На это <b>{CAPTCHA_TIMEOUT} сек.</b>"
        )

        try:
            await captcha_service.start(
                chat_id=event.chat.id,
                user=member,
                reply_markup=get_captcha_kb(member.id),
                text=text,
            )
        except CaptchaError:
            return
        return

    await _send_welcome(event, chat_service)

@router.callback_query(F.data.startswith("captcha_"), OwnerCallbackFilter())
@inject
async def captcha_passed(
    callback: CallbackQuery,
    chat_service: ChatService = Provide[Container.chat_service],
    captcha_service: CaptchaService = Provide[Container.captcha_service]
) -> None:
    if callback.message is None:
        await callback.answer()
        return

    chat_id = callback.message.chat.id

    try:
        await captcha_service.verify(chat_id, callback.from_user.id)
    except CaptchaError as e:
        await callback.answer(str(e), show_alert=False)
        return

    await callback.answer()

    welcome = await chat_service.get_welcome_message(telegram_id=chat_id)

    if not welcome:
        return

    text = welcome.replace("{name}", escape(callback.from_user.first_name))

    try:
        await callback.bot.send_message(chat_id=chat_id, text=text)
    except TelegramAPIError as e:
        error_logger.warning(f"[CHAT] Welcome message failed | chat_id={chat_id} | error={e}")

@router.chat_join_request()
async def approve_join_request(event: ChatJoinRequest) -> None:
    if event.chat.type not in ("group", "supergroup"):
        return

    try:
        await event.approve()
    except TelegramAPIError as e:
        error_logger.warning(
            f"[CHAT] Join request approve failed | chat_id={event.chat.id} "
            f"| user_id={event.from_user.id} | {e}"
        )

async def _send_welcome(event: ChatMemberUpdated, chat_service: ChatService) -> None:
    welcome_message = await chat_service.get_welcome_message(telegram_id=event.chat.id)

    if not welcome_message:
        return

    text = welcome_message.replace("{name}", escape(event.new_chat_member.user.first_name))

    try:
        await event.bot.send_message(chat_id=event.chat.id, text=text)
    except TelegramAPIError as e:
        error_logger.warning(f"[CHAT] Welcome message failed | chat_id={event.chat.id} | error={e}")