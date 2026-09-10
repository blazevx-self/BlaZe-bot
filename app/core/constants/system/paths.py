from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent.parent.parent
BASE_DIR = APP_DIR.parent

YAML_PATH = APP_DIR / 'configs' / 'config.yaml'
ENV_PATH = BASE_DIR / '.env'
FONT_PATH = APP_DIR / "assets" / "fonts" / "Rubik.ttf"
WORDLE_WORDS_PATH = APP_DIR / "assets" / "wordle" / "words.txt"
QUIZ_PATH = APP_DIR / "assets" / "json" / "quiz.json"
EMOJI_FONT_PATH = APP_DIR / "assets" / "fonts" / "NotoColorEmoji.ttf"