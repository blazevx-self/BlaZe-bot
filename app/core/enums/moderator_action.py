from enum import StrEnum

class ModerationActionType(StrEnum):
    WARN = "warn"
    UNWARN = "unwarn"
    MUTE = "mute"
    UNMUTE = "unmute"
    BAN = "ban"
    UNBAN = "unban"
    KICK = "kick"