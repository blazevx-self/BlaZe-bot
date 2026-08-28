import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.configs.settings import settings

from app.bot.routers.routes import all_routers
from app.database.database import (
    session_factory,
    create_tables,
    engine,
    reset_session
)

from app.utils.logger import system_logger

from app.bot.middleware.logging_middleware import LoggingMiddleware
from app.bot.middleware.antispam_middleware import AntiSpamGhoulMiddleware
from app.bot.middleware.antiflood_middleware import AntifloodMiddleware
from app.bot.middleware.sync_entities_middleware import SyncEntitiesMiddleware
from app.bot.middleware.ban_middleware import BanMiddleware
from app.bot.middleware.database_middleware import DatabaseMiddleware

async def on_startup():
    system_logger.info("[SYSTEM] Bot started | version=1.0.0 | py=%s", sys.version.split()[0])

async def on_shutdown():
    system_logger.info("[SYSTEM] Bot stopped")

async def setup_middlewares(dp: Dispatcher) -> None:
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    dp.message.middleware(DatabaseMiddleware(session_factory=session_factory))
    dp.callback_query.middleware(DatabaseMiddleware(session_factory=session_factory))

    dp.message.middleware(SyncEntitiesMiddleware())
    dp.callback_query.middleware(SyncEntitiesMiddleware())

    dp.message.middleware(BanMiddleware())

    dp.callback_query.middleware(AntiSpamGhoulMiddleware(time_limit=0.7))

    dp.message.middleware(AntifloodMiddleware(limit_seconds=5, max_requests=15))
    dp.callback_query.middleware(AntifloodMiddleware(limit_seconds=5, max_requests=15))

async def init_database(reset: bool = False):
    if reset:
        await reset_session(engine)
        system_logger.info("[DB] Database reset")
    else:
        await create_tables(engine)
        system_logger.info("[DB] Database initialized")

async def main():
    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True
        )
    )

    try:
        await init_database(reset=False)

        dp = Dispatcher()

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