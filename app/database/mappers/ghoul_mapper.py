from app.database.models.ghoul import GhoulOrm
from app.types.entities.ghoul import GhoulData

def orm_to_ghoul(ghoul: GhoulOrm) -> GhoulData:
    return GhoulData(
        telegram_id=ghoul.telegram_id,
        
        name=ghoul.name,
        level=ghoul.level,
        rc_money=ghoul.rc_money,
        
        snap_count=ghoul.snap_count,
        coffee_count=ghoul.coffee_count,

        kagune_type=ghoul.kagune_type,
        kagune_strength=ghoul.kagune_strength,
        kagune_was_obtained=ghoul.kagune_was_obtained,

        strength=ghoul.strength,
        dexterity=ghoul.dexterity,
        speed=ghoul.speed,
        hp=ghoul.hp,
        regen=ghoul.regen,

        eat_humans=ghoul.eat_humans,
        eat_ghouls=ghoul.eat_ghouls,

        is_kakuja=ghoul.is_kakuja
    )