from datetime import timedelta

LINK_ENTITY_TYPES = {"url", "text_link"}

MIN_MESSAGES_FOR_LINKS = 100
LINK_STRIKES_TTL = timedelta(hours=24)
LINK_MUTE_DURATION = timedelta(hours=10)
NOTICE_TTL_SECONDS = 15

DANGEROUS_LINK_PATTERNS = (
    # приглашения в чужие чаты/каналы
    "t.me/+", "t.me/joinchat", "telegram.me/joinchat",
    # сокращатели — за ними прячут фишинг
    "bit.ly", "tinyurl.com", "cutt.ly", "clck.ru", "goo.su", "is.gd", "t.ly",
    # исполняемые файлы
    ".apk", ".exe",
)