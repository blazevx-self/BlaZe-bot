import logging
from pathlib import Path

from rich.logging import RichHandler
from logging.handlers import TimedRotatingFileHandler


# Форматтеры для файлов и красивого цветного терминала
FILE_FORMATTER = logging.Formatter("[%(asctime)s] %(levelname)s | %(message)s", datefmt="%H:%M:%S")
CONSOLE_FORMATTER = logging.Formatter("%(message)s")


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

    log_path = Path(file_path)
    log_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    file_handler = TimedRotatingFileHandler(
        filename=log_path,
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


def get_logger(name: str, folder: str, level=logging.INFO):
    return setup_file_logger(
        name=name,
        file_path=f"logs/{folder}/{name}.log",
        level=level
    )


bot_logger = get_logger("bot", "bot")
callback_logger = get_logger("callbacks", "callbacks")
system_logger = get_logger("system", "system")

security_logger = get_logger("security", "security")
error_logger = get_logger("errors", "errors")

start_logger = get_logger("start", "game")

quiz_logger = get_logger("quiz", "game")

snap_logger = get_logger("snap", "game")
coffee_logger = get_logger("coffee", "game")
kagune_logger = get_logger("kagune", "game")
stats_logger = get_logger("stats", "game")
