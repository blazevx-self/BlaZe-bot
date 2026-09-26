from app.bot.routers.ghoul import kagune, snap, coffee, stats, race_profile
from app.bot.routers.common import (
    start, help, bot,
    unknown_commands, profile, balance,
    transfer, error, id_user,
)

from app.bot.routers.game import quiz, wordle, lottery
from app.bot.routers.tops import top_bal, top_click, top_kagune, top_coffee

from app.bot.routers.chat.moderator import (
    rules, welcome_message, goodbye_message,
    ban_chat, kick, mute, warn, history_moderator
)
from app.bot.routers.chat.chat_member_update import new_chat_member, left_chat_member
from app.bot.routers.chat.common import rp_commands, report, list_admins

from app.bot.routers.admin import ban_bot, modify_balance, player_lookup, field_edit, reset, broadcast

all_routers = (
    start.router,
    help.router,
    bot.router,
    balance.router,
    transfer.router,
    id_user.router,

    coffee.router,
    kagune.router,
    snap.router,
    stats.router,

    race_profile.router,
    profile.router,

    wordle.router,
    quiz.router,
    lottery.router,

    top_bal.router,
    top_click.router,
    top_kagune.router,
    top_coffee.router,

    new_chat_member.router,
    left_chat_member.router,

    ban_bot.router,
    modify_balance.router,
    player_lookup.router,
    field_edit.router,
    reset.router,
    broadcast.router,

    rules.router,
    goodbye_message.router,
    welcome_message.router,
    ban_chat.router,
    kick.router,
    mute.router,
    warn.router,
    history_moderator.router,
    rp_commands.router,
    report.router,
    list_admins.router,

    error.router,

    unknown_commands.router,
)

__all__ = ["all_routers"]