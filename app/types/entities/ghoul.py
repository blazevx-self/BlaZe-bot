from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=True)
class GhoulData:    
    telegram_id: int

    hunger_updated_at: datetime

    rc_money: int
    level: int = 1

    snap_count: int = 0
    coffee_count: int = 0

    kagune_type: str | None = None
    kagune_strength: int = 0
    kagune_was_obtained: bool = False

    strength: int = 1
    dexterity: int = 1
    speed: int = 1
    hp: int = 5
    regen: int = 5

    eat_humans: int = 0
    eat_ghouls: int = 0

    hunger: int = 100
    
    is_kakuja: bool = False