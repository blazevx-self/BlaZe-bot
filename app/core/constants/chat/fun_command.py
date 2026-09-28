import re

BOT_PREFIX = r"^бот[,\s]+"

PICK_MEMBER_PATTERN = re.compile(rf"{BOT_PREFIX}(?:выбери|выбирай)\b.*\bучастник", re.IGNORECASE)
PICK_PATTERN = re.compile(rf"{BOT_PREFIX}(?:выбери|выбирай)\s+(?P<options>.+)$", re.IGNORECASE | re.DOTALL)
WHO_PATTERN = re.compile(rf"{BOT_PREFIX}кто\s+(?P<question>.+?)\??$", re.IGNORECASE | re.DOTALL)
CHANCE_PATTERN = re.compile(
    rf"{BOT_PREFIX}(?:вероятность|шанс)\s+(?:того\s+)?(?:что\s+)?(?P<question>.+?)\??$",
    re.IGNORECASE | re.DOTALL,
)

RATE_PATTERN = re.compile(rf"{BOT_PREFIX}оцени\s+(?P<subject>.+?)\??$", re.IGNORECASE | re.DOTALL)
WHEN_PATTERN = re.compile(rf"{BOT_PREFIX}когда\s+(?P<question>.+?)\??$", re.IGNORECASE | re.DOTALL)
NUMBER_PATTERN = re.compile(rf"{BOT_PREFIX}число\s+(?P<low>-?\d+)\s+(?P<high>-?\d+)\s*$", re.IGNORECASE)
COUPLE_PATTERN = re.compile(rf"{BOT_PREFIX}пара\s+дня\s*$", re.IGNORECASE)

OPTIONS_SEPARATOR = re.compile(r"\s*(?:,|\bили\b)\s*", re.IGNORECASE)
MAX_OPTIONS = 20
MAX_TEXT_LENGTH = 200
MAX_WHEN_DAYS = 3650

HOW_MUCH_PATTERN = re.compile(rf"{BOT_PREFIX}насколько\s+я\s+(?P<quality>.+?)\??$", re.IGNORECASE | re.DOTALL)
TOP_PATTERN = re.compile(rf"{BOT_PREFIX}топ\s+(?P<title>.+?)\s*$", re.IGNORECASE | re.DOTALL)
COUNT_PATTERN = re.compile(rf"{BOT_PREFIX}сколько\s+(?P<question>.+?)\??$", re.IGNORECASE | re.DOTALL)
COIN_PATTERN = re.compile(rf"{BOT_PREFIX}(?:монетка|монета|орёл или решка|орел или решка)\s*$", re.IGNORECASE)
DICE_PATTERN = re.compile(rf"{BOT_PREFIX}(?:кубик|кости)\s*$", re.IGNORECASE)

TOP_SIZE = 5
MAX_COUNT = 1000