from app.utils.format_num import format_num
from app.services.ghoul_service import ghoul_service
from app.core.templates.common.profile_template import profile_text

# noinspection PyMethodMayBeStatic
class ProfileService:
    """Сервис формирования обычного профиля пользователя"""

    async def build_profile(self, user: dict) -> dict:
        """Формирует текст профиля с текущими характеристиками пользователя"""

        user_id = user['user_id']
        first_name = user['name']
        level = user['level']

        link = f'<a href="tg://user?id={user_id}"><b>{first_name}</b></a>'

        status = ghoul_service.get_status(user)
        rank = ghoul_service.get_rank(level)

        money = format_num(user.get('money', 0))
        clicks = format_num(user.get('clicks') or 0)
        coffee = format_num(user.get("coffee_total") or 0)

        text = profile_text(
            user_link=link,
            level=level,
            rank=rank,
            status=status,
            money=money,
            clicks=clicks,
            coffee=coffee
        )

        return {'text': text}

profile_service = ProfileService()