import asyncio
import sys

from aiogram import Bot, Dispatcher
from app.configs.settings import settings

from app.bot.routers.routes import all_routers

from app.bot.middleware.logging_middleware import LoggingMiddleware
from app.bot.middleware.antispam_middleware import AntiSpamGhoulMiddleware
from app.bot.middleware.antiflood_middleware import AntifloodMiddleware
from app.bot.middleware.db_middleware import DatabaseMiddleware

from app.utils.logger import system_logger
from app.database.init_db import init_db

bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
dp = Dispatcher()

async def on_startup():
    system_logger.info("[SYSTEM] Bot started | version=1.0.0 | py=%s", sys.version.split()[0])

async def on_shutdown():
    system_logger.warning("[SYSTEM] Bot stopped")

async def main():
    try:
        system_logger.info("[SYSTEM] Initializing database...")
        await init_db()
        system_logger.info("[SYSTEM] Database initialized")

        dp.message.middleware(LoggingMiddleware())
        dp.callback_query.middleware(LoggingMiddleware())

        dp.message.middleware(AntifloodMiddleware(limit_seconds=5, max_requests=15))
        dp.callback_query.middleware(AntifloodMiddleware(limit_seconds=5, max_requests=15))

        dp.callback_query.middleware(AntiSpamGhoulMiddleware(time_limit=0.7))

        dp.message.middleware(DatabaseMiddleware())
        dp.callback_query.middleware(DatabaseMiddleware())

        dp.include_routers(*all_routers)

        await on_startup()
        system_logger.info("[SYSTEM] Polling started")

        await dp.start_polling(bot)

    except Exception as e:
        system_logger.exception(f"[SYSTEM] Fatal error: {e}")
        raise

    finally:
        await on_shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        system_logger.info("[SYSTEM] Bot interrupted by user")
