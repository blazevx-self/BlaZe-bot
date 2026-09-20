from html import escape

from aiogram import Router

from aiogram.types import ChatMemberUpdated, LinkPreviewOptions
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    IS_MEMBER, IS_NOT_MEMBER,
)
from aiogram.exceptions import TelegramAPIError

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.configs.game import game_cfg

from app.database.repositories.chat_repository import ChatRepository

from app.services.chat.chat_service import ChatService
from app.bot.keyboards.common.help_keyboard import get_help_menu

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

    if event.new_chat_member.user.id != (await event.bot.get_me()).id:
        return

    await chat_repo.upsert(
        telegram_id=event.chat.id,
        title=event.chat.title,
        username=event.chat.username
    )

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
    chat_service: ChatService = Provide[Container.chat_service]
) -> None:
    if event.chat.type not in ("group", "supergroup"):
        return

    member = event.new_chat_member.user
    welcome_message = await chat_service.get_welcome_message(telegram_id=event.chat.id)

    if not welcome_message:
        return

    welcome_message = welcome_message.replace(
        "{name}",
        escape(member.first_name)
    )

    await event.bot.send_message(chat_id=event.chat.id, text=welcome_message)