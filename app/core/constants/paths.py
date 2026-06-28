from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

YAML_PATH = BASE_DIR / 'config.yaml'
ENV_PATH = BASE_DIR / '.env'

DB_PATH = BASE_DIR / 'app' / 'database' / 'database.db'

LOGS_DIR = [
    BASE_DIR / "logs",
    BASE_DIR / "logs" / "bot",
    BASE_DIR / "logs" / "errors",
    BASE_DIR / "logs" / "callbacks",
    BASE_DIR / "logs" / "security",
    BASE_DIR / "logs" / "system",
    BASE_DIR / "logs" / "services",
    BASE_DIR / "logs" / "performance"
]