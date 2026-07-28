from app.core.templates.common.profile_template import profile_text
from app.core.enums import ResultStatus

from app.types.services_result.common import ProfileResult
from app.types.entities import UserData


from app.utils.format_num import format_num
from app.utils.truncate_name import truncate_text

from app.services.ghoul_service import ghoul_service

class ProfileService:
    """Сервис формирования обычного профиля пользователя"""

    @staticmethod
    async def build_profile(user: UserData) -> ProfileResult:
        """Формирует текст профиля с текущими характеристиками пользователя"""

        user_id = user.user_id
        first_name = user.name
        level = user.level

        link = f'<a href="tg://user?id={user_id}"><b>{truncate_text(first_name)}</b></a>'

        status = ghoul_service.get_status(user)
        rank = ghoul_service.get_rank(level)

        money = format_num(user.money)
        snap = format_num(user.snap)
        coffee = format_num(user.coffee_total)

        text = profile_text(
            user_link=link,
            level=level,
            rank=rank,
            status=status,
            money=money,
            snap=snap,
            coffee=coffee
        )

        return ProfileResult(
            status=ResultStatus.SUCCESS,
            text=text
        )

profile_service = ProfileService()