from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


while BASE_DIR != BASE_DIR.parent:
    if BASE_DIR.name == "BlaZe-bot":
        break
    BASE_DIR = BASE_DIR.parent
else:
    raise RuntimeError("Project root not found")


YAML_PATH = BASE_DIR / 'config.yaml'
ENV_PATH = BASE_DIR / '.env'
FONT_PATH = BASE_DIR / "app" /"assets" / "fonts" / "Rubik.ttf"
WORDLE_WORDS_PATH = "app/assets/wordle/words.txt"