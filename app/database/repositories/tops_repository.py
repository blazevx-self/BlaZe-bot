from sqlalchemy import select, func

from app.database.repositories.base import Base

from app.database.models.user import UserOrm
from app.database.models.ghoul import GhoulOrm

class TopsRepository(Base):
    async def get_top(self, top_type: str, limit: int):
        if top_type == "money":
            stmt = (
                select(UserOrm)
                .where(UserOrm.money > 0)
                .order_by(UserOrm.money.desc())
                .limit(limit)
            )
        
        elif top_type == "snap":
            stmt = (
                select(GhoulOrm)
                .where(GhoulOrm.snap_count > 0)
                .order_by(GhoulOrm.snap_count.desc())
                .limit(limit)
            )
        
        elif top_type == "kagune":
            stmt = (
                select(GhoulOrm)
                .where(GhoulOrm.kagune_strength > 0)
                .order_by(GhoulOrm.kagune_strength.desc())
                .limit(limit)
            )
                    
        elif top_type == "coffee":
            stmt = (
                select(GhoulOrm)
                .where(GhoulOrm.coffee_count > 0)
                .order_by(GhoulOrm.coffee_count.desc())
                .limit(limit)
            )   
        
        else:
            raise ValueError(f"Unknown top type: {top_type}")
         
        result = await self.session.scalars(stmt)
        
        return list(result)

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