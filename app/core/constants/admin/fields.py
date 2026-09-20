from app.core.enums.cooldown_action import CooldownAction

ALLOWED_USER_FIELDS = {
    'money',

    'is_banned',
    'ban_reason',
    'banned_until',

    'quiz_reset_date',
    'quiz_questions_left'
}

ALLOWED_GHOUL_FIELDS = {
    'rc_money',
    'level',

    'snap_count',
    'coffee_count',

    'kagune_strength',
    'kagune_was_obtained',

    'strength',
    'dexterity',
    'speed',
    'hp',
    'regen',

    'eat_humans',
    'eat_ghouls',

    'is_kakuja',
}

ALLOWED_COOLDOWN_FIELDS: dict[str, CooldownAction] = {
    "snap_cooldown": CooldownAction.SNAP,
    "coffee_cooldown": CooldownAction.COFFEE,
    "coffee_overdose_cooldown": CooldownAction.COFFEE_OVERDOSE,
    "kagune_cooldown": CooldownAction.KAGUNE_GROW,
}