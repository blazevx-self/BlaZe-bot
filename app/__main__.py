import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.configs.settings import settings

from app.bot.routers.routes import all_routers
from app.utils.logger import system_logger

from app.bot.middleware.logging_middleware import LoggingMiddleware
from app.bot.middleware.antispam_middleware import AntiSpamGhoulMiddleware
from app.bot.middleware.antiflood_middleware import AntifloodMiddleware
from app.bot.middleware.user_sync_middleware import UserSyncMiddleware

from app.database.init_db import init_db

async def on_startup():
    system_logger.info("[SYSTEM] Bot started | version=1.0.0 | py=%s", sys.version.split()[0])

async def on_shutdown():
    system_logger.info("[SYSTEM] Bot stopped")

async def setup_middlewares(dp: Dispatcher) -> None:
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    dp.message.middleware(UserSyncMiddleware())
    dp.callback_query.middleware(UserSyncMiddleware())

    dp.callback_query.middleware(AntiSpamGhoulMiddleware(time_limit=0.7))

    dp.message.middleware(AntifloodMiddleware(limit_seconds=5, max_requests=15))
    dp.callback_query.middleware(AntifloodMiddleware(limit_seconds=5, max_requests=15))

async def main():
    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True
        )
    )

    try:
        dp = Dispatcher()

        await init_db()
        await setup_middlewares(dp)

        dp.include_routers(*all_routers)
        system_logger.info("[SYSTEM] Loaded %d routers", len(all_routers))

        system_logger.info("[SYSTEM] Starting polling...")
        await dp.start_polling(bot, on_startup=on_startup, on_shutdown=on_shutdown)

    except Exception as e:
        system_logger.exception(f"[SYSTEM] Fatal error: {e}")
        raise

    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        system_logger.info("[SYSTEM] Interrupted by Ctrl+C")
