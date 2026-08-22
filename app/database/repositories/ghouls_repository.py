from typing import Any

from sqlalchemy import select, update, func, exists
from sqlalchemy.dialects.postgresql import insert

from app.database.models.ghoul import GhoulOrm
from app.database.repositories.base import Base

from app.core.constants.game.stats import ALLOWED_STATS
from app.utils.logger import system_logger

class GhoulRepository(Base):
    async def upsert(self, telegram_id: int, **kwargs: Any) -> GhoulOrm:
        values = {"telegram_id": telegram_id, **kwargs}
        
        update_dict = {
            k: v for k, v in values.items()
            if k not in ["id", "telegram_id", "became_ghoul_at"]
        }     
        
        if not update_dict:
            update_dict = {"updated_at": func.now()} 
        else:
            update_dict["updated_at"] = func.now()
            
        stmt = (
            insert(GhoulOrm)
            .values(**values)
            .on_conflict_do_update(
                index_elements=[GhoulOrm.telegram_id],
                set_=update_dict
            )
            .returning(GhoulOrm)
        )
        
        ghoul = await self.session.scalar(stmt)
        
        if ghoul is None:
            system_logger.error(f"Ghoul ({telegram_id}) not found after upsert operation")
            raise ValueError(f"Ghoul ({telegram_id}) not found")
        
        return ghoul
    
    
    async def get(self, telegram_id: int) -> GhoulOrm | None:
        stmt = select(GhoulOrm).where(GhoulOrm.telegram_id == telegram_id)
        return await self.session.scalar(stmt)
    
    
    async def get_by_id(self, ghoul_id: int) -> GhoulOrm | None:
        stmt = select(GhoulOrm).where(GhoulOrm.id == ghoul_id)
        return await self.session.scalar(stmt)
    
    
    async def exists(self, telegram_id: int) -> bool:
        stmt = select(exists().where(GhoulOrm.telegram_id == telegram_id))
        return await self.session.scalar(stmt)
    
    
    async def init_kagune(self, telegram_id: int, kagune_type: str) -> GhoulOrm:
        stmt = (
            update(GhoulOrm)
            .where(
                GhoulOrm.telegram_id == telegram_id,
                GhoulOrm.kagune_was_obtained.is_(False)
            )
            .values(
                kagune_type=kagune_type,
                kagune_strength=1,
                kagune_was_obtained=True
            )
            .returning(GhoulOrm)
        )
        
        ghoul = await self.session.scalar(stmt)
                
        if ghoul is None:
            raise ValueError(f"Cannot initialize kagune for ghoul ({telegram_id})")
                
        return ghoul
    
    
    async def update_kagune_strength(self, telegram_id: int, new_strength: int) -> GhoulOrm:
        stmt = (
            update(GhoulOrm)
            .where(GhoulOrm.telegram_id == telegram_id)
            .values(kagune_strength=new_strength)
            .returning(GhoulOrm)
        )
        
        ghoul = await self.session.scalar(stmt)
        
        if ghoul is None:
            raise ValueError(f"Ghoul ({telegram_id}) not found") 
        
        return ghoul
            
    
    async def increment_snap_count(self, telegram_id: int, timestamp: int) -> GhoulOrm:
        stmt = (
            update(GhoulOrm)
            .where(GhoulOrm.telegram_id == telegram_id)
            .values(snap_count=GhoulOrm.snap_count + 1)
            .returning(GhoulOrm)
        )
        
        ghoul = await self.session.scalar(stmt)
        
        if ghoul is None:
            raise ValueError(f"Ghoul ({telegram_id}) not found")
        
        return ghoul
    
    
    async def increment_coffee_count(self, telegram_id: int, timestamp: int) -> GhoulOrm:
        stmt = (
            update(GhoulOrm)
            .where(GhoulOrm.telegram_id == telegram_id)
            .values(coffee_count=GhoulOrm.coffee_count + 1)
        )
        
        ghoul = await self.session.scalar(stmt)
        
        if ghoul is None:
            raise ValueError(f"Ghoul ({telegram_id}) not found")
        
        return ghoul
    
    
    async def upgrade_stat(self, telegram_id: int, stat: str, amount: str) -> GhoulOrm:
        if stat not in ALLOWED_STATS:
            raise ValueError(f"Unknown stat: {stat}")
        
        stat_column = getattr(GhoulOrm, stat)
        
        stmt = (
            update(GhoulOrm)
            .where(GhoulOrm.telegram_id == telegram_id)
            .values({stat_column: stat_column + amount})
            .returning(GhoulOrm)
        )
        
        ghoul = await self.session.scalar(stmt)
        
        if ghoul is None:
            raise ValueError(f"Ghoul ({telegram_id}) not found")
        
        return ghoul