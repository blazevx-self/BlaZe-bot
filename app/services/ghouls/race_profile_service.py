from app.services.ghoul_service import ghoul_service
from app.core.templates.ghoul.race_profile_template import race_profile_text

# noinspection PyMethodMayBeStatic

class RaceProfileService:
    async def build_race_profile(self, user: dict):
        power = ghoul_service.calculate_power(user)
        danger_rank = ghoul_service.get_danger_rank(power)

        link = (
            f'<a href="tg://user?id={user["user_id"]}">'
            f'<b>{user["name"]}</b></a>'
        )

        text = race_profile_text(
            user=user,
            user_link=link,
            danger_rank=danger_rank,
            level=user["level"],
            power=power,
            kagune_lvl=user["kagune_lvl"]
        )

        return {"text": text}

race_service = RaceProfileService()