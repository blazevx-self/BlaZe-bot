from html import escape

from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from app.configs.game import game_cfg

from app.core.constants.chat.count_warn import MAX_WARNINGS
from app.core.templates.common.profile import profile_text
from app.core.enums import ResultStatus

from app.types.services_result.common import ProfileResult
from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.database.repositories.chat.chat_member import ChatMemberRepository

from app.utils.format_num import format_num
from app.utils.truncate_text import truncate_text
from app.utils.time import days_since_registration

class ProfileService:
    def __init__(self, bot: Bot, chat_member_repo: ChatMemberRepository):
        self.bot = bot
        self.chat_member_repo = chat_member_repo

    @staticmethod
    def get_status(days_in_project: int) -> str:
        """Определяет статус пользователя по его общей активности в проекте."""

        statuses = game_cfg.profile_statuses.statuses

        profile_score = days_in_project
        current_status = "Новичок"

        for threshold in sorted(statuses):
            if profile_score >= threshold:
                current_status = statuses[threshold]
            else:
                break

        return current_status

    async def build_chat_block(self, chat_id: int, user_id: int) -> str:
        """Блок «В этом чате» для профиля в группе."""

        member = await self.bot.get_chat_member(chat_id, user_id)

        if member.status == ChatMemberStatus.CREATOR:
            role = "Создатель"
        elif member.status == ChatMemberStatus.ADMINISTRATOR:
            role = "Администратор"
        else:
            role = "Участник"

        db_member = await self.chat_member_repo.get_by_telegram_ids(chat_id, user_id)

        warnings = db_member.warnings if db_member else 0
        messages = format_num(db_member.messages_count) if db_member else 0
        since = db_member.created_at.strftime("%d.%m.%Y") if db_member else "—"

        return (
            "\n<tg-emoji emoji-id=\"6030784887093464891\">💬</tg-emoji> <b>В этом чате</b>\n"
            f"└ <b>Роль:</b> <code>{role}</code>\n"
            f"└ <b>Предупреждения:</b> <code>{warnings}/{MAX_WARNINGS}</code>\n"
            f"└ <b>Сообщений:</b> <code>{messages}</code>\n"
            f"└ <b>В чате с:</b> <code>{since}</code>\n"
        )

    @staticmethod
    async def build_profile(
        user: UserData,
        ghoul: GhoulData,
        chat_block: str = ""
    ) -> ProfileResult:
        user_id = user.telegram_id
        link = (
            f'<a href="tg://user?id={user_id}">'
            f'<b>{escape(truncate_text(user.name))}</b></a>'
        )

        days_in_project = days_since_registration(created_at=user.created_at)
        status = ProfileService.get_status(days_in_project=days_in_project)
        
        race = "Гуль" if ghoul.kagune_was_obtained else "Человек"

        text = profile_text(
            user_link=link,
            user_id=user_id,
            race=race,
            status=status,
            money=format_num(user.money),
            registered_at=user.created_at.strftime("%d.%m.%Y %H:%M"),
            days_in_project=days_in_project,
            chat_block=chat_block
        )

        return ProfileResult(
            status=ResultStatus.SUCCESS,
            text=text
        )