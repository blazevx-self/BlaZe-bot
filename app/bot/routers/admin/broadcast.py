from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from dependency_injector.wiring import inject, Provide

from app.containers import Container

from app.services.admin.broadcast import BroadcastService
from app.bot.filters.admin import AdminFilter

from app.utils.logger import admin_logger

router = Router()

@router.message(Command("broadcast"), AdminFilter())
@inject
async def broadcast_cmd(
    message: Message,
    broadcast_service: BroadcastService = Provide[Container.broadcast_service]
) -> None:
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.reply(
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            "<b>Использование:</b>\n"
            "/broadcast private «текст»\n"
            "/broadcast chats «текст»\n"
            "/broadcast all «текст»\n"
            "/broadcast user «@username» «текст»"
        )
        return

    target = args[1].lower()
    text = args[2]

    status = await message.reply(
        "<tg-emoji emoji-id=\"6039573425268201570\">📤</tg-emoji>"
        "Рассылка запущена..."
    )

    if target == "user":
        sub = text.split(maxsplit=1)

        if len(sub) < 2:
            await status.edit_text(
                "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> "
                "Укажи получателя и текст."
            )
            return

        ok = await broadcast_service.send_to_target(sub[0], sub[1])

        await status.edit_text(
            "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
            "Отправлено" if ok else "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> "
            "Не удалось отправить (пользователь заблокирован / не найден)"
        )

        return

    try:
        if target == "private":
            result = await broadcast_service.broadcast_to_private(text)
        elif target == "chats":
            result = await broadcast_service.broadcast_to_chats(text)
        elif target == "all":
            result = await broadcast_service.broadcast_to_all(text)
        else:
            await status.edit_text(
                "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> "
                "Неизвестная цель рассылки."
            )
            return

    except Exception as e:
        admin_logger.exception(f"[BROADCAST] Failed")
        await status.edit_text(
            "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> "
            f"Ошибка рассылки: {e}"
        )
        return

    await status.edit_text(
        "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
        "<b>Рассылка завершена.</b>\n\n"
        f"<b>Всего:</b> <code>{result.total}</code> | "
        f"<b>Успешно:</b> <code>{result.success}</code> | "
        f"<b>Ошибок:</b> <code>{result.failed}</code>"
    )