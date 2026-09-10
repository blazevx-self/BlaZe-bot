from datetime import datetime
from dataclasses import dataclass

from app.core.enums.rp_commands import TypeRpCommand

@dataclass
class RpCommandResult:
    id: int
    command: str
    action: str
    type_command: TypeRpCommand
    file_id: str | None
    created_at: datetime