import aiogram.exceptions

from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from app.configs.yaml_loader import cfg
from app.configs.game import game_cfg

from app.core.enums import ResultStatus
from app.core.exceptions.user import UserNotFoundError

from app.types.services_result.common import StartResult
from app.types.entities.user import UserData

from app.database.repositories.user_repository import UserRepository
from app.utils.logger import start_logger

class StartService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def start(self, user: UserData, bot: Bot) -> StartResult:
        """Проверяет подписку пользователя и выдаёт стартовый бонус.

        Если бонус уже был получен или пользователь не подписан,
        возвращает стандартное приветственное сообщение.
        """

        user_id = user.telegram_id

        if user.is_subscribed:
            return StartResult(
                status=ResultStatus.SUCCESS,
                text=(
                    f"<tg-emoji emoji-id='5289581576001167896'>🤨</tg-emoji> "
                    f"{cfg['message']['start']}"
                ),
            )

        #Проверка подписки на канал через Telegram API
        try:
            member = await bot.get_chat_member(
                chat_id=game_cfg.start.channel_id,
                user_id=user_id
            )

            is_subscribed = member.status in (
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR,
            )

        except aiogram.exceptions.TelegramAPIError as e:
            start_logger.warning(f"[START] Subscription check failed | user_id={user_id} | error={e}")
            is_subscribed = False

        if is_subscribed:
            bonus = game_cfg.start.bonus_amount

            try:
                await self.user_repo.activate_subscribed_bonus(telegram_id=user_id, bonus=bonus)
            except UserNotFoundError:
                pass
            else:
                start_logger.info(f"[START] Subscription bonus issued | user_id={user_id} | bonus={bonus}")

                return StartResult(
                    status=ResultStatus.SUCCESS,
                    text=cfg['message']['text_is_subscription'].format(bonus_money=bonus)
                )

        text = f"<tg-emoji emoji-id='5289581576001167896'>🤨</tg-emoji> {cfg['message']['start']}"

        return StartResult(
            status=ResultStatus.SUCCESS,
            text=text
        )