from sqlalchemy import select, func

from app.database.repositories.base import Base

from app.database.models.user import UserOrm
from app.database.models.ghoul import GhoulOrm

from app.database.mappers.user_mapper import orm_to_user
from app.database.mappers.ghoul_mapper import orm_to_ghoul

from app.types.services_result.tops import TopUser

class TopsRepository(Base):
    async def get_top(self, top_type: str, limit: int) -> list[TopUser]:
        if top_type == "money":
            value_column = UserOrm.money

        elif top_type == "snap":
            value_column = GhoulOrm.snap_count

        elif top_type == "kagune":
            value_column = GhoulOrm.kagune_strength

        elif top_type == "coffee":
            value_column = GhoulOrm.coffee_count

        else:
            raise ValueError(f"Unknown top type: {top_type}")

        stmt = (
            select(UserOrm, GhoulOrm)
            .outerjoin(
                GhoulOrm,
                GhoulOrm.telegram_id == UserOrm.telegram_id
            )
            .where(value_column > 0)
            .order_by(value_column.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return [
            TopUser(
                user=orm_to_user(user),
                ghoul=orm_to_ghoul(ghoul) if ghoul else None
            )
            for user, ghoul in result.all()
        ]

    async def get_rank(self, telegram_id: int, top_type: str) -> int | None:
        if top_type == "money":
            model = UserOrm
            value_column = UserOrm.money

        elif top_type == "snap":
           model = GhoulOrm
           value_column = GhoulOrm.snap_count

        elif top_type == "kagune":
            model = GhoulOrm
            value_column = GhoulOrm.kagune_strength

        elif top_type == "coffee":
            model = GhoulOrm
            value_column = GhoulOrm.coffee_count

        else:
            raise ValueError(f"Unknown top type: {top_type}")
        
        rank = func.rank().over(order_by=value_column.desc()).label("rank")
        
        ranked = (
            select(
                model.telegram_id,
                rank
            )
            .where(value_column > 0)
            .subquery()
        )
        
        stmt = select(ranked.c.rank).where(ranked.c.telegram_id == telegram_id)
        
        return await self.session.scalar(stmt)