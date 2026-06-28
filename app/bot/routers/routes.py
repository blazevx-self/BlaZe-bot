from aiogram import Router

from app.bot.routers.ghoul import kagune, click, coffee, stats, race_profile
from app.bot.routers.common import start, help, ping, unknown_commands, profile, balance, topbal
from app.bot.routers.chat_member_update import new_chat_member
from app.bot.routers.game import quiz

main_router = Router()

all_routers = (
    start.router,
    help.router,
    new_chat_member.router,
    coffee.router,
    kagune.router,
    ping.router,
    balance.router,
    click.router,
    topbal.router,
    quiz.router,
    profile.router,
    race_profile.router,
    stats.router,
    unknown_commands.router,
)

__all__ = ["all_routers"]