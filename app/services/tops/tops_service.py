import asyncio

from app.configs.game import game_cfg
from app.core.enums import ResultStatus

from app.types.services_result.tops import TopResult
from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.database.repositories.tops_repository import TopsRepository

class TopsService:
    def __init__(self, tops_repo: TopsRepository):
        self.tops_repo = tops_repo

    async def tops(
        self,
        user: UserData,
        top_type: str,
        ghoul: GhoulData | None = None
    ) -> TopResult:
        limit = game_cfg.tops.get_limit(top_type)

        leaderboard, rank = await asyncio.gather(
            self.tops_repo.get_top(
                top_type=top_type,
                limit=limit
            ),
            self.tops_repo.get_rank(
                telegram_id=user.telegram_id,
                top_type=top_type
            )
        )

        return TopResult(
            status=ResultStatus.SUCCESS,
            user=user,
            ghoul=ghoul,
            top_user=leaderboard,
            rank=rank or 0
        )