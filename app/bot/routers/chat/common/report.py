from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.core.exceptions.chat import ReportError

from app.services.chat.common.report import ReportService
from app.bot.filters.group_only import GroupOnlyFilter

router = Router()

@router.message(Command("report"), GroupOnlyFilter())
@inject
async def report_cmd(
    message: Message,
    report_service: ReportService = Provide[Container.report_service]
):
    if not message.text or not message.from_user:
        return

    reply = message.reply_to_message

    if not reply or not reply.from_user:
        await message.reply(
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            "<b>Использование:</b> ответьте на сообщение нарушителя командой "
            "/report [причина]"
        )
        return

    # сообщение от имени самого чата = анонимный админ
    if reply.sender_chat and reply.sender_chat.id == message.chat.id:
        await message.reply(
            "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
            "Нельзя пожаловаться на администратора."
        )
        return

    args = message.text.split(maxsplit=1)
    reason = args[1] if len(args) > 1 else None

    try:
        moderators = await report_service.report(
            chat_id=message.chat.id,
            reporter_id=message.from_user.id,
            target=reply.from_user
        )
    except ReportError as e:
        await message.reply(str(e))
        return

    await message.reply(report_service.fmt_report(reply.from_user, moderators, reason))