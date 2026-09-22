from app.core.enums import ResultStatus
from app.core.templates.ghoul.race_profile import race_profile_text

from app.types.services_result.ghoul import RaceProfileResult
from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.services.ghouls.ghoul import GhoulService
from app.utils.truncate_name import truncate_text

class RaceProfileService:
    def __init__(self, ghoul_service: GhoulService):
        self.ghoul_service = ghoul_service

    async def build_race_profile(self, user: UserData, ghoul: GhoulData) -> RaceProfileResult:
        power = self.ghoul_service.calculate_power(ghoul)
        danger_rank = self.ghoul_service.get_danger_rank(power)

        link = (
            f'<a href="tg://user?id={user.telegram_id}">'
            f'<b>{truncate_text(user.name)}</b></a>'
        )

        text = race_profile_text(
            ghoul=ghoul,
            user_link=link,
            danger_rank=danger_rank,
            level=ghoul.level,
            power=power,
            kagune_lvl=ghoul.kagune_strength,
            snap=ghoul.snap_count,
            coffee=ghoul.coffee_count
        )

        return RaceProfileResult(
            status=ResultStatus.SUCCESS,
            text=text
        )