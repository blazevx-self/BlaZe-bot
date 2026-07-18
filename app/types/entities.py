from dataclasses import dataclass

@dataclass(slots=True)
class UserData:
    user_id: int
    name: str
    username: str | None = None
    is_subscribed: bool = False
    money: int = 0

    clicks: int = 0
    last_click: int = 0

    coffee_cooldown: int = 0
    coffee_last_time: int = 0
    coffee_total: int = 0

    level: int = 1

    kagune_was_obtained: bool = False
    kagune_lvl: int=0
    kagune_type: str | None = None
    kagune_last_grow: int = 0
    kakuja_activated: bool = False

    strength: int = 1
    agility: int = 1
    speed: int = 1
    hp: int = 1
    regen: int = 1
