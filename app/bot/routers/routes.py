from app.bot.routers.ghoul import kagune, snap, coffee, stats, race_profile
from app.bot.routers.common import start, help, ping, unknown_commands, profile, balance
from app.bot.routers.game import quiz
from app.bot.routers.tops import top_bal, top_click, top_kagune
from app.bot.routers.chat import rules, new_chat_member, welcome_message

all_routers = (
    start.router,
    help.router,
    ping.router,
    balance.router,
    profile.router,

    coffee.router,
    kagune.router,
    snap.router,

    quiz.router,

    top_bal.router,
    top_click.router,
    top_kagune.router,
    race_profile.router,
    stats.router,

    new_chat_member.router,
    rules.router,
    welcome_message.router,

    unknown_commands.router,
)

__all__ = ["all_routers"]