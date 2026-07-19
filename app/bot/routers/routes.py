from aiogram import Router

from app.bot.routers.ghoul import kagune, snap, coffee, stats, race_profile
from app.bot.routers.common import start, help, ping, unknown_commands, profile, balance
from app.bot.routers.chat_member_update import new_chat_member
from app.bot.routers.game import quiz
from app.bot.routers.tops import top_bal, top_click, top_kagune

main_router = Router()

all_routers = (
    start.router,
    help.router,
    new_chat_member.router,
    ping.router,
    balance.router,
    profile.router,
    unknown_commands.router,

    coffee.router,
    kagune.router,
    snap.router,

    top_bal.router,
    top_click.router,
    top_kagune.router,
    race_profile.router,
    stats.router,

    quiz.router,
)

__all__ = ["all_routers"]