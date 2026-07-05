import yaml

from app.core.constants.system.paths import YAML_PATH
from app.utils.logger import system_logger

def load_config() -> dict:
    system_logger.info(f"[CONFIG] Loading...")

    if not YAML_PATH.exists():
        system_logger.error(f"[CONFIG] File not found: {YAML_PATH}")
        raise FileNotFoundError(f"Config file not found: {YAML_PATH}")

    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        try:
            data = yaml.safe_load(f)

        except yaml.YAMLError as e:
            system_logger.error(F"[CONFIG] Invalid YAML: {e}")
            raise ValueError(f"Invalid YAML: {e}")

        if data is None:
            system_logger.error("[CONFIG] Empty file")
            raise ValueError("Config is empty")

    system_logger.info(f"[CONFIG] Loaded (3 root sections)")

    return data

cfg = load_config()

