from app.core.enums import ResultStatus
from app.types.services_types.common import TopBalResult

from app.database.repositories.users_repository import user_repository

# noinspection PyMethodMayBeStatic
class TopService:
    """Сервис получения рейтингов игрока по внутриигровой валюте."""

    async def process_top(self, user: dict) -> TopBalResult:
        """Возвращает таблицу лидеров и позицию пользователя."""

        return TopBalResult(
            status=ResultStatus.SUCCESS,
            top_user=await user_repository.get_user_top(15),
            rank=await user_repository.get_user_rank(user["user_id"]),
            user=user
        )

top_service = TopService()