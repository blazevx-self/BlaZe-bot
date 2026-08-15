from app.configs.yaml import cfg
from app.configs.game import game_cfg

HELP_TEXT = cfg['message']['help']['help_text']

# шаблон для /help
def build_help_text() -> str:
    link = game_cfg.start.guide_link
    return f'<a href="{link}">\u200b</a><tg-emoji emoji-id="5289508548672234708">😇</tg-emoji> ' + HELP_TEXT

