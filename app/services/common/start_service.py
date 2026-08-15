import aiogram.exceptions

from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from app.configs.yaml import cfg
from app.configs.game import game_cfg

from app.core.enums import ResultStatus

from app.types.services_result.common import StartResult
from app.types.entities import UserData

from app.database.repositories.users_repository import user_repository
from app.utils.logger import start_logger

class StartService:
    """Сервис обработки команды /start."""

    @staticmethod
    async def process_start(user: UserData, bot: Bot) -> StartResult:
        """Проверяет подписку пользователя и выдаёт стартовый бонус.

        Если бонус уже был получен или пользователь не подписан,
        возвращает стандартное приветственное сообщение.
        """

        user_id = user.user_id

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

        if is_subscribed and not user.is_subscribed:
            bonus = game_cfg.start.bonus_amount

            await user_repository.activate_subscribed_bonus(user_id=user_id, bonus=bonus)
            
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

start_service = StartService()