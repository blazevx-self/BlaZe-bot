import logging
from pathlib import Path

from rich.logging import RichHandler
from logging.handlers import TimedRotatingFileHandler

from app.core.constants.paths import LOGS_DIR

# Форматтеры для файлов и красивого цветного терминала
FILE_FORMATTER = logging.Formatter("[%(asctime)s] %(levelname)s | %(message)s", datefmt="%H:%M:%S")
CONSOLE_FORMATTER = logging.Formatter("%(message)s")

for path in LOGS_DIR:
    Path(path).mkdir(parents=True, exist_ok=True)

def setup_file_logger(
        name: str,
        file_path: str,
        level=logging.INFO
) -> logging.Logger:
    """Создаёт папки для логов,
    настраивает ротацию файлов и выводит красивый
    форматированный лог в консоль через RichHandler.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    file_handler = TimedRotatingFileHandler(
        filename=file_path,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
        errors="ignore",
        delay=True
    )
    file_handler.setFormatter(FILE_FORMATTER)
    file_handler.setLevel(level)

    console_handler = RichHandler(
        level=level,
        rich_tracebacks=True,
        markup=True,
        show_time=True
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

bot_logger = setup_file_logger(
    "bot",
    "logs/bot/bot.log", logging.INFO
)

error_logger = setup_file_logger(
    "errors",
    "logs/errors/errors.log", logging.ERROR
)

callback_logger = setup_file_logger(
    "callbacks",
    "logs/callbacks/callbacks.log", logging.INFO
)

security_logger = setup_file_logger(
    "security",
    "logs/security/security.log", logging.WARNING
)

system_logger = setup_file_logger(
    "system",
    "logs/system/system.log", logging.INFO
)

service_logger = setup_file_logger(
    "service",
    "logs/service/service.log", logging.INFO
)

performance_logger = setup_file_logger(
    "performance",
    "logs/performance/performance.log", logging.WARNING
)

__all__ = (
    "bot_logger",
    "callback_logger",
    "error_logger",
    "security_logger",
    "system_logger",
    "service_logger",
    "performance_logger"
)