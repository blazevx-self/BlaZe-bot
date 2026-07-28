from app.bot.routers.ghoul import kagune, snap, coffee, stats, race_profile
from app.bot.routers.common import start, help, ping, unknown_commands, profile, balance

from app.bot.routers.game import quiz
from app.bot.routers.tops import top_bal, top_click, top_kagune

from app.bot.routers.chat.moderator import rules, welcome_message, goodbye_message
from app.bot.routers.chat.chat_member_update import new_chat_member, left_chat_member

all_routers = (
    start.router,
    help.router,
    ping.router,
    balance.router,


    coffee.router,
    kagune.router,
    snap.router,
    stats.router,

    race_profile.router,
    profile.router,

    quiz.router,

    top_bal.router,
    top_click.router,
    top_kagune.router,

    new_chat_member.router,
    left_chat_member.router,

    rules.router,
    goodbye_message.router,
    welcome_message.router,

    unknown_commands.router,
)

__all__ = ["all_routers"]