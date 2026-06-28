import asyncio

from aiogram import Bot, Dispatcher
from app.configs.sqlalchemy_cfg import settings

from app.bot.routers.routes import all_routers

from app.bot.middleware.logging_middleware import LoggingMiddleware
from app.bot.middleware.antispam_middleware import AntiSpamGhoulMiddleware
from app.bot.middleware.antiflood_middleware import AntifloodMiddleware
from app.bot.middleware.db_middleware import DatabaseMiddleware

from app.utils.logger import system_logger
from app.database.init_db import init_db

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()

async def on_startup():
    system_logger.info("[SYSTEM] Bot started")

async def on_shutdown():
    system_logger.warning("[SYSTEM] Bot stopped")

async def main():
    await init_db()

    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    dp.message.middleware(AntifloodMiddleware(limit_seconds=5, max_requests=15))
    dp.callback_query.middleware(AntifloodMiddleware(limit_seconds=5, max_requests=15))

    dp.callback_query.middleware(AntiSpamGhoulMiddleware(time_limit=0.7))

    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())

    dp.include_routers(*all_routers)

    await on_startup()

    try:
        await dp.start_polling(bot)

    finally:
        await on_shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print('Bot stopped')
