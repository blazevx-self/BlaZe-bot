from app.configs.yaml import cfg

HELP_TEXT = cfg['message']['help']['help_text']

# шалон для /help
def build_help_text() -> str:
    link = cfg['settings']['guide_link']

    return (
            f'<a href="{link}">\u200b</a><tg-emoji emoji-id="5289508548672234708">😇</tg-emoji> ' + HELP_TEXT
    )
