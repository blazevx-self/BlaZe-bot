from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=True)
class UserData:
    telegram_id: int
    name: str
    created_at: datetime
    username: str | None = None
    
    money: int = 0
    
    is_subscribed: bool = False
    
    is_banned: bool = False
    ban_reason: str | None = None
    banned_until: datetime | None = None