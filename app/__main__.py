import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.containers import Container
from app.configs.settings import settings

from app.database.database import (
    session_factory,
    create_tables,
    engine,
    reset_session
)

from app.bot.middlewares import (
    BanMiddleware,
    AntiSpamGhoulMiddleware,
    LoggingMiddleware,
    AntifloodMiddleware,
    DatabaseMiddleware,
    SyncEntitiesMiddleware,
)

from app.bot.routers.routes import all_routers
from app.services.backup import daily_backup
from app.questions_loader import seed_quiz_questions

from app.utils.logger import system_logger
from app.utils.logger import database_logger

async def on_startup():
    system_logger.info("[SYSTEM] Bot started | version=1.0.5 | py=%s", sys.version.split()[0])

async def on_shutdown():
    system_logger.info("[SYSTEM] Bot stopped")

async def setup_middlewares(dp: Dispatcher) -> None:
    dp.update.middleware(DatabaseMiddleware(session_factory=session_factory))

    dp.message.middleware(SyncEntitiesMiddleware())
    dp.callback_query.middleware(SyncEntitiesMiddleware())

    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    dp.message.middleware(BanMiddleware())

    dp.callback_query.middleware(AntiSpamGhoulMiddleware(time_limit=1.0))

    dp.message.middleware(AntifloodMiddleware(limit_seconds=5, max_requests=15))
    dp.callback_query.middleware(AntifloodMiddleware(limit_seconds=5, max_requests=15))

async def init_database(reset: bool = False):
    if reset:
        await reset_session(engine)
        database_logger.info("[DB] Database reset")
    else:
        await create_tables(engine)
        database_logger.info("[DB] Database initialized")

    await seed_quiz_questions()

async def main():
    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True
        )
    )

    container = Container(bot=bot)

    container.wire(
        modules=[__name__],
        packages=[
            "app.bot.routers",
            "app.bot.middlewares",
            "app.bot.filters",
        ]
    )

    try:
        await init_database(reset=False)

        dp = Dispatcher()

        await setup_middlewares(dp)

        dp.include_routers(*all_routers)
        system_logger.info("[SYSTEM] Loaded %d routers", len(all_routers))

        asyncio.create_task(daily_backup(bot))

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