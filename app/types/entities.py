from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class UserData:
    user_id: int
    name: str
    created_at: datetime
    username: str | None = None
    is_subscribed: bool = False
    money: int = 0
    is_banned: bool = False
    ban_reason: str | None = None
    banned_until: datetime | None = None

    snap: int = 0
    last_snap: int = 0

    coffee_cooldown: int = 0
    coffee_last_time: int = 0
    coffee_total: int = 0

    level: int = 1

    kagune_was_obtained: bool = False
    kagune_lvl: int = 0
    kagune_type: str | None = None
    kagune_last_grow: int = 0
    kakuja_activated: bool = False

    strength: int = 1
    agility: int = 1
    speed: int = 1
    hp: int = 1
    regen: int = 1
