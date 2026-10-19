from app.bot.routers.ghoul import (
    kagune, snap, coffee, stats,
    race_profile, hunger, eat_human
)

from app.bot.routers.common import (
    start, help, bot, profile, balance,
    transfer, daily_bonus, anime
)

from app.bot.routers.system import error, catch_all, unknown_commands

from app.bot.routers.game import quiz, wordle, lottery
from app.bot.routers.tops import top_bal, top_click, top_kagune, top_coffee

from app.bot.routers.chat.moderator import (
    rules, welcome_message, goodbye_message,
    ban_chat, kick, mute, warn, history_moderator,
    admin_chat, captcha_enabled
)
from app.bot.routers.chat.chat_member_update import new_chat_member, left_chat_member
from app.bot.routers.chat.common import rp_commands, report, list_admins, ai, fun_commands

from app.bot.routers.admin import (
    ban_bot, modify_balance, player_lookup,
    field_edit, reset, broadcast, add_gif,
    kill_ghoul,
)

all_routers = (
    # user
    start.router,
    help.router,
    bot.router,
    balance.router,
    profile.router,
    transfer.router,
    daily_bonus.router,
    anime.router,

    # ghoul
    coffee.router,
    kagune.router,
    snap.router,
    stats.router,
    race_profile.router,
    hunger.router,
    eat_human.router,

    # game
    wordle.router,
    quiz.router,
    lottery.router,

    # tops
    top_bal.router,
    top_click.router,
    top_kagune.router,
    top_coffee.router,

    # chat member update
    new_chat_member.router,
    left_chat_member.router,

    # administrator
    ban_bot.router,
    modify_balance.router,
    player_lookup.router,
    field_edit.router,
    reset.router,
    broadcast.router,
    add_gif.router,
    kill_ghoul.router,

    # moderator
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
    fun_commands.router,
    ai.router,
    admin_chat.router,
    captcha_enabled.router,

    error.router,

    unknown_commands.router,

    catch_all.router,
)

__all__ = ["all_routers"]