from datetime import datetime
from dataclasses import dataclass

from app.core.enums.moderator_action import ModerationActionType
from app.core.enums.rp_commands import TypeRpCommand

from app.types.entities.user import UserData

@dataclass
class RpCommandResult:
    id: int
    command: str
    action: str
    type_command: TypeRpCommand
    file_id: str | None
    created_at: datetime

@dataclass
class ModeratorActionResult:
    action: ModerationActionType
    user: UserData
    reason: str | None = None
    until: datetime | None = None
    warnings: int | None = None

@dataclass
class HistoryEntry:
    action: ModerationActionType
    reason: str | None
    until: datetime | None
    created_at: datetime
    moderator_name: str | None

@dataclass
class HistoryResult:
    user: UserData
    entries: list[HistoryEntry]