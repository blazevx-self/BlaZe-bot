import yaml

from app.core.constants.paths import YAML_PATH

def load_config() -> dict:
    if not YAML_PATH.exists():
        raise FileNotFoundError(f"Файл конфигурации не найден: {YAML_PATH}")

    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

cfg = load_config()

