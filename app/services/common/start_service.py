import aiogram.exceptions

from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from app.configs.yaml import cfg
from app.core.enums import ResultStatus
from app.types.services_types.common import StartResult

from app.database.repositories.users_repository import user_repository

# noinspection PyMethodMayBeStatic
class StartService:
    """Сервис обработки команды /start."""

    async def process_start(self, user: dict, bot: Bot) -> StartResult:
        """Проверяет подписку пользователя и выдаёт стартовый бонус.

        Если бонус уже был получен или пользователь не подписан,
        возвращает стандартное приветственное сообщение.
        """

        user_id = user['user_id']
        is_subscribed = False

        #Проверка подписки на канал через Telegram API
        try:
            member = await bot.get_chat_member(
                chat_id=cfg['settings']['channel_id'],
                user_id=user_id
            )

            if member.status in (
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR,
            ):
                is_subscribed = True

        except aiogram.exceptions.TelegramAPIError:
            is_subscribed = False

        if is_subscribed and not user.get('is_subscribed'):
            bonus = cfg['settings']['bonus_amount']
            await user_repository.activate_subscribed_bonus(user_id, bonus)

            new_money = user.get('money', 0) + bonus

            return StartResult(
                status=ResultStatus.SUCCESS,
                text=cfg['settings']['text_is_subscription'].format(bonus_money=bonus),
                new_money=new_money,
                is_subscribed = True
            )

        raw_text = cfg['message']['start']
        text = f"<tg-emoji emoji-id='5289581576001167896'>🤨</tg-emoji> {raw_text}"

        return StartResult(
            status=ResultStatus.SUCCESS,
            text=text
        )

start_service = StartService()