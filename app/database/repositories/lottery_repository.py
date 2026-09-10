from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

from app.database.repositories.base import Base
from app.database.models.lottery import LotteryOrm

class LotteryRepository(Base):
    async def insert(
        self,
        telegram_id: int,
        bet_amount: int,
        chosen_color: str,
        winning_color: str,
        is_won: bool,
        earned: int
    ) -> LotteryOrm:
        stmt = (
            insert(LotteryOrm)
            .values(
                telegram_id=telegram_id,
                bet_amount=bet_amount,
                chosen_color=chosen_color,
                winning_color=winning_color,
                is_won=is_won,
                earned=earned
            )
            .returning(LotteryOrm)
        )

        lottery = await self.session.scalar(stmt)

        if not lottery:
            raise ValueError("Failed to create an entry in the betting history..")

        return lottery

    async def get_by_id(self, lottery_id: int) -> LotteryOrm | None:
        stmt = select(LotteryOrm).where(LotteryOrm.id == lottery_id)
        return await self.session.scalar(stmt)

    async def get_by_user_id(self, telegram_id: int) -> list[LotteryOrm]:
        stmt = (
            select(LotteryOrm)
            .where(LotteryOrm.telegram_id == telegram_id)
            .order_by(LotteryOrm.created_at.desc())
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def get_recent_by_user_id(self, telegram_id: int, limit: int = 10) -> list[LotteryOrm]:
        stmt = (
            select(LotteryOrm)
            .where(LotteryOrm.telegram_id == telegram_id)
            .order_by(LotteryOrm.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def delete_by_id(self, lottery_id: int) -> bool:
        stmt = (
            delete(LotteryOrm)
            .where(LotteryOrm.id == lottery_id)
            .returning(LotteryOrm.id)
        )

        deleted_id = await self.session.scalar(stmt)

        return deleted_id is not None