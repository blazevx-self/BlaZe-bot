from aiogram import Router, F
from aiogram.types import Message

router = Router()
router.message.filter(F.chat.type.in_({"group", "supergroup"}))

@router.message()
async def catch_all(message: Message) -> None:
    """Ничего не делает.

    Нужен, чтобы inner-middleware (синхронизация, счётчик сообщений)
    срабатывали и на обычные сообщения в группах, а не только на команды.
    """