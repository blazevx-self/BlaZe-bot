from app.core.enums import ResultStatus
from app.core.templates.ghoul.race_profile_template import race_profile_text

from app.types.entities import UserData
from app.types.services_result.ghoul import RaceProfileResult

from app.services.ghoul_service import ghoul_service
from app.utils.truncate_name import truncate_text


class RaceProfileService:
    """Сервис формирования расового профиля игрока."""

    @staticmethod
    async def build_race_profile(user: UserData) -> RaceProfileResult:
        """Формирует расовый профиль гуля.

        Вычисляет суммарную мощь, ранг угрозы и собирает текст профиля.
        """

        power = ghoul_service.calculate_power(user)
        danger_rank = ghoul_service.get_danger_rank(power)

        link = (
            f'<a href="tg://user?id={user.user_id}">'
            f'<b>{truncate_text(user.name)}</b></a>'
        )

        text = race_profile_text(
            user=user,
            user_link=link,
            danger_rank=danger_rank,
            level=user.level,
            power=power,
            kagune_lvl=user.kagune_lvl
        )

        return RaceProfileResult(
            status=ResultStatus.SUCCESS,
            text=text
        )

race_service = RaceProfileService()