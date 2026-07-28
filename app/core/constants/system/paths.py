from pathlib import Path


BASE_DIR = Path(__file__).resolve()

while BASE_DIR.name != "BlaZe bot V2":
    BASE_DIR = BASE_DIR.parent

YAML_PATH = BASE_DIR / 'config.yaml'
ENV_PATH = BASE_DIR / '.env'

DB_PATH = BASE_DIR / 'app' / 'database' / 'database.db'

