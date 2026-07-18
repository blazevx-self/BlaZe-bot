import asyncio

from app.core.enums import ResultStatus
from app.configs.game import game_cfg

from app.types.entities import UserData
from app.types.services_types.tops import TopResult

from app.database.repositories.tops_repository import tops_repository

# noinspection PyMethodMayBeStatic
class TopsService:
    """Сервис получения рейтингов игрока в топах."""

    async def process_tops(
            self,
            user: UserData,
            top_type: str,
    ) -> TopResult:
        """Возвращает таблицу лидеров и позицию пользователя."""

        limit = game_cfg.tops.get_limit(top_type)

        leaderboard, rank = await asyncio.gather(
            tops_repository.get_top(
                top_type=top_type,
                limit=limit
            ),
            tops_repository.get_rank(
                user_id=user.user_id,
                top_type=top_type
            )
        )

        return TopResult(
            status=ResultStatus.SUCCESS,
            top_user=leaderboard,
            rank=rank,
            user=user
        )

top_service = TopsService()