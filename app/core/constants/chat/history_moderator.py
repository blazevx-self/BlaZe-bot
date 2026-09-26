from app.core.enums.moderator_action import ModerationActionType

HISTORY_LIMIT = 10

ACTION_ICONS = {
    ModerationActionType.WARN: "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji>",
    ModerationActionType.UNWARN: "<tg-emoji emoji-id=\"5895507195524550741\">↩️</tg-emoji>",
    ModerationActionType.MUTE: "<tg-emoji emoji-id=\"5258267368877989660\">🔇</tg-emoji> ",
    ModerationActionType.UNMUTE: "<tg-emoji emoji-id=\"5260325873688518261\">🔊</tg-emoji>",
    ModerationActionType.BAN: "<tg-emoji emoji-id=\"5258318620722733379\">🚫</tg-emoji> ",
    ModerationActionType.UNBAN: "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> ",
    ModerationActionType.KICK: "<tg-emoji emoji-id=\"6030329749409108167\">💬</tg-emoji>",
}