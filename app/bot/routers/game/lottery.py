import re
import asyncio

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile

from dependency_injector.wiring import Provide, inject
from app.containers import Container

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.services.game.lottery.lottery import LotteryService

from app.utils.logger import lottery_logger

router = Router()

DEP_PATTERN = r"^депнуть\s+(\S+)\s+(\d+)$"

@router.message(F.text.lower().startswith("депнуть"))
@inject
async def dep_cmd(
    message: Message,
    user: UserData,
    ghoul: GhoulData,
    lottery_service: LotteryService = Provide[Container.lottery_service]
):
    if not message.from_user or not message.text:
        return

    match = re.fullmatch(DEP_PATTERN, message.text.lower().strip())

    if not match:
        await message.reply(
            "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji> "
            "<b>Использование:</b> депнуть «цвет» «ставка»"
        )
        return

    color_str = match.group(1)
    bet_amount = int(match.group(2))

    try:
        chosen_color = lottery_service.parse_color(color_str)

        result = await lottery_service.execute(
            user=user,
            ghoul=ghoul,
            chosen_color=chosen_color,
            bet_amount=bet_amount
        )

    except ValueError as e:
        await message.reply(str(e))
        return

    except Exception:
        lottery_logger.exception(f"[LOTTERY] Error processing bet | user_id={message.from_user.id}")

        await message.reply(
            "<tg-emoji emoji-id=\"5260342697075416641\">❌</tg-emoji>"
            "<b>Не удалось обработать ставку.</b> Попробуйте ещё раз."
        )
        return

    await message.answer_animation(
        animation=BufferedInputFile(
            result.video,
            filename="lottery.mp4"
        )
    )

    await asyncio.sleep(6)

    await message.answer(
        result.text,
        reply_to_message_id=message.message_id
    )