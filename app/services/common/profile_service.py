from app.configs.game import game_cfg

from app.core.templates.common.profile_template import profile_text
from app.core.enums import ResultStatus

from app.types.services_result.common import ProfileResult
from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.utils.format_num import format_num
from app.utils.truncate_name import truncate_text
from app.utils.time import days_since_registration

class ProfileService:
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

    @staticmethod
    async def build_profile(user: UserData, ghoul: GhoulData) -> ProfileResult:
        user_id = user.telegram_id
        link = f'<a href="tg://user?id={user_id}"><b>{truncate_text(user.name)}</b></a>'

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
        )

        return ProfileResult(
            status=ResultStatus.SUCCESS,
            text=text
        )