import aiogram.exceptions

from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from app.configs.yaml import cfg

from app.database.repositories.users_repository import user_repository
from app.utils.user import update_user

# noinspection PyUnusedLocal
# noinspection PyMethodMayBeStatic
class StartService:
    async def process_start(self, user: dict, bot: Bot) -> str:
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

            user = update_user(
                user,
                money=user.get("money", 0) + bonus,
                is_subscribed=1
            )

            return cfg['settings']['text_is_subscription'].format(bonus_money=bonus)

        raw_text = cfg['message']['start']

        return (
            f'<tg-emoji emoji-id="5289581576001167896">🤨</tg-emoji> '
            f'{raw_text}'
        )

start_service = StartService()