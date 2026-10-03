from app.core.enums.daily_bonus import BonusReward, EffectKey
from app.core.enums.cooldown_action import CooldownAction

R = BonusReward

ALL_REWARDS: frozenset[BonusReward] = frozenset(BonusReward.__members__.values())

# Что нужно, чтобы награда могла выпасть
GHOUL_REWARDS: frozenset[BonusReward] = frozenset({
    R.RESET_SNAP, R.RESET_COFFEE, R.FAST_SNAP, R.FAST_COFFEE,
    R.PENALTY_SNAP, R.PENALTY_COFFEE, R.SNAP_COUNT, R.COFFEE_COUNT,
    R.RESET_ALL, R.FAST_ALL, R.STAT_UP, R.STATS_DISCOUNT, R.STATS_PRICE_UP,
})

KAGUNE_REWARDS: frozenset[BonusReward] = frozenset({
    R.RESET_KAGUNE, R.FAST_KAGUNE, R.PENALTY_KAGUNE,
    R.KAGUNE_LEVEL, R.KAGUNE_DISCOUNT, R.KAGUNE_PRICE_UP,
})

# награда -> поле диапазона в DailyBonusConfig
MONEY_RANGES: dict[BonusReward, str] = {
    R.MONEY_SMALL: "money_small",
    R.MONEY_MEDIUM: "money_medium",
    R.MONEY_JACKPOT: "money_jackpot",
}

# награда -> какие кулдауны сбросить
RESETS: dict[BonusReward, tuple[CooldownAction, ...]] = {
    R.RESET_SNAP: (CooldownAction.SNAP,),
    R.RESET_COFFEE: (CooldownAction.COFFEE, CooldownAction.COFFEE_OVERDOSE),
    R.RESET_KAGUNE: (CooldownAction.KAGUNE_GROW,),
    R.RESET_ALL: (
        CooldownAction.SNAP,
        CooldownAction.COFFEE,
        CooldownAction.COFFEE_OVERDOSE,
        CooldownAction.KAGUNE_GROW,
    ),
}

# награда -> к какому кулдауну добавить штраф
PENALTIES: dict[BonusReward, CooldownAction] = {
    R.PENALTY_SNAP: CooldownAction.SNAP,
    R.PENALTY_COFFEE: CooldownAction.COFFEE,
    R.PENALTY_KAGUNE: CooldownAction.KAGUNE_GROW,
}

# награда -> (колонка гуля, поле диапазона в DailyBonusConfig)
COUNTERS: dict[BonusReward, tuple[str, str]] = {
    R.SNAP_COUNT: ("snap_count", "counts"),
    R.COFFEE_COUNT: ("coffee_count", "counts"),
    R.KAGUNE_LEVEL: ("kagune_strength", "kagune_levels"),
}

# награда -> (эффекты, поле диапазона множителя в DailyBonusConfig)
EFFECTS: dict[BonusReward, tuple[tuple[EffectKey, ...], str]] = {
    R.FAST_SNAP: ((EffectKey.SNAP_COOLDOWN,), "fast_multiplier"),
    R.FAST_COFFEE: ((EffectKey.COFFEE_COOLDOWN,), "fast_multiplier"),
    R.FAST_KAGUNE: ((EffectKey.KAGUNE_COOLDOWN,), "fast_multiplier"),
    R.FAST_ALL: (
        (EffectKey.SNAP_COOLDOWN, EffectKey.COFFEE_COOLDOWN, EffectKey.KAGUNE_COOLDOWN),
        "fast_multiplier",
    ),
    R.KAGUNE_DISCOUNT: ((EffectKey.KAGUNE_PRICE,), "discount_multiplier"),
    R.STATS_DISCOUNT: ((EffectKey.STATS_PRICE,), "discount_multiplier"),
    R.KAGUNE_PRICE_UP: ((EffectKey.KAGUNE_PRICE,), "price_up_multiplier"),
    R.STATS_PRICE_UP: ((EffectKey.STATS_PRICE,), "price_up_multiplier"),
    R.QUIZ_REWARD_BOOST: ((EffectKey.QUIZ_REWARD,), "quiz_boost_multiplier"),
}

# Короткие названия — для показа «что было в остальных коробках»
BONUS_LABELS: dict[BonusReward, str] = {
    BonusReward.MONEY_SMALL: "<tg-emoji emoji-id=\"5258204546391351475\">💰</tg-emoji> Немного BC",
    BonusReward.MONEY_MEDIUM: "<tg-emoji emoji-id=\"5258204546391351475\">💰</tg-emoji> Много BC",
    BonusReward.MONEY_JACKPOT: "<tg-emoji emoji-id=\"5386698912641870515\">💎</tg-emoji> Джекпот",
    BonusReward.MONEY_LOSS: "<tg-emoji emoji-id=\"5472030678633684592\">💸</tg-emoji> Потеря BC",

    BonusReward.QUIZ_QUESTIONS: "<tg-emoji emoji-id=\"6030848053177486888\">❓</tg-emoji> Доп. вопросы",
    BonusReward.QUIZ_RESET: "<tg-emoji emoji-id=\"6030848053177486888\">❓</tg-emoji> Сброс викторины",
    BonusReward.QUIZ_REWARD_BOOST: "<tg-emoji emoji-id=\"6030848053177486888\">❓</tg-emoji> Буст викторины",

    BonusReward.RESET_SNAP: "<tg-emoji emoji-id=\"5834596128246469018\">🫰</tg-emoji> Сброс щелчка",
    BonusReward.RESET_COFFEE: "<tg-emoji emoji-id=\"5386470514871003633\">☕️</tg-emoji> Вторая чашка",
    BonusReward.RESET_KAGUNE: "<tg-emoji emoji-id=\"5442804822048780010\">😫</tg-emoji> Сброс кагуне",
    BonusReward.RESET_ALL: "<tg-emoji emoji-id=\"5260687119092817530\">🔄</tg-emoji> Сброс всего",

    BonusReward.FAST_SNAP: "<tg-emoji emoji-id=\"5877203642636832557\">⏩</tg-emoji> Быстрый щелчок",
    BonusReward.FAST_COFFEE: "<tg-emoji emoji-id=\"5877203642636832557\">⏩</tg-emoji> Быстрый кофе",
    BonusReward.FAST_KAGUNE: "<tg-emoji emoji-id=\"5877203642636832557\">⏩</tg-emoji> Быстрое кагуне",
    BonusReward.FAST_ALL: "<tg-emoji emoji-id=\"5877203642636832557\">⏩</tg-emoji> Всё быстрее",

    BonusReward.PENALTY_SNAP: "<tg-emoji emoji-id=\"5834571187371381456\">💢</tg-emoji> Штраф щелчка",
    BonusReward.PENALTY_COFFEE: "<tg-emoji emoji-id=\"5834571187371381456\">💢</tg-emoji> Штраф кофе",
    BonusReward.PENALTY_KAGUNE: "<tg-emoji emoji-id=\"5834571187371381456\">💢</tg-emoji> Штраф кагуне",

    BonusReward.SNAP_COUNT: "<tg-emoji emoji-id=\"5834596128246469018\">🫰</tg-emoji> + щелчки",
    BonusReward.COFFEE_COUNT: "<tg-emoji emoji-id=\"5386470514871003633\">☕️</tg-emoji> + кофе",
    BonusReward.KAGUNE_LEVEL: "<tg-emoji emoji-id=\"5442804822048780010\">😫</tg-emoji> + уровень кагуне",
    BonusReward.STAT_UP: "<tg-emoji emoji-id=\"5834929920219812289\">💪</tg-emoji> + стат",

    BonusReward.KAGUNE_DISCOUNT: "<tg-emoji emoji-id=\"5888620056551625531\">🏷</tg-emoji> Скидка на кагуне",
    BonusReward.STATS_DISCOUNT: "<tg-emoji emoji-id=\"5888620056551625531\">🏷</tg-emoji> Скидка на статы",
    BonusReward.KAGUNE_PRICE_UP: "<tg-emoji emoji-id=\"5875012827063783367\">📈</tg-emoji> Кагуне дороже",
    BonusReward.STATS_PRICE_UP: "<tg-emoji emoji-id=\"5875012827063783367\">📈</tg-emoji> Статы дороже",

    BonusReward.EMPTY: "<tg-emoji emoji-id=\"5834948255435198932\">🕳</tg-emoji> Пусто",
}

BONUS_TEXTS: dict[BonusReward, str] = {
    BonusReward.MONEY_SMALL: "<tg-emoji emoji-id=\"5258204546391351475\">💰</tg-emoji> В коробке лежало <b>{amount}</b> BC!",
    BonusReward.MONEY_MEDIUM: "<tg-emoji emoji-id=\"5258204546391351475\">💰</tg-emoji> Отличный улов: <b>{amount}</b> BC!",
    BonusReward.MONEY_JACKPOT: "<tg-emoji emoji-id=\"5386698912641870515\">💎</tg-emoji> <b>ДЖЕКПОТ!</b> Ты получил <b>{amount}</b> BC!",
    BonusReward.MONEY_LOSS: "<tg-emoji emoji-id=\"5472030678633684592\">💸</tg-emoji> Из коробки выскочил вор и утащил <b>{amount}</b> BC.",

    BonusReward.QUIZ_QUESTIONS: "<tg-emoji emoji-id=\"6030848053177486888\">❓</tg-emoji> +<b>{amount}</b> вопросов викторины на сегодня!",
    BonusReward.QUIZ_RESET: "<tg-emoji emoji-id=\"6030848053177486888\">❓</tg-emoji> Викторина сброшена — вопросы снова доступны!",
    BonusReward.QUIZ_REWARD_BOOST: "<tg-emoji emoji-id=\"6030848053177486888\">❓</tg-emoji> Награда за викторину <b>+{percent}%</b> на <b>{time}</b>!",

    BonusReward.RESET_SNAP: "<tg-emoji emoji-id=\"5920515922505765329\">⚡️</tg-emoji> Кулдаун щелчка сброшен!",
    BonusReward.RESET_COFFEE: "<tg-emoji emoji-id=\"5386470514871003633\">☕️</tg-emoji> Можно выпить ещё одну чашку — кофе и передоз сброшены!",
    BonusReward.RESET_KAGUNE: "<tg-emoji emoji-id=\"5260687681733533075\">🔃</tg-emoji> Кулдаун кагуне сброшен!",
    BonusReward.RESET_ALL: "<tg-emoji emoji-id=\"5260687119092817530\">🔄</tg-emoji> <b>Все кулдауны сброшены!</b> Щелчок, кофе, кагуне и викторина.",

    BonusReward.FAST_SNAP: "<tg-emoji emoji-id=\"5877203642636832557\">⏩</tg-emoji> Кулдаун щелчка <b>−{percent}%</b> на <b>{time}</b>!",
    BonusReward.FAST_COFFEE: "<tg-emoji emoji-id=\"5877203642636832557\">⏩</tg-emoji> Кулдаун кофе <b>−{percent}%</b> на <b>{time}</b>!",
    BonusReward.FAST_KAGUNE: "<tg-emoji emoji-id=\"5877203642636832557\">⏩</tg-emoji> Кулдаун кагуне <b>−{percent}%</b> на <b>{time}</b>!",
    BonusReward.FAST_ALL: "<tg-emoji emoji-id=\"5877203642636832557\">⏩</tg-emoji> <b>Все кулдауны −{percent}%</b> на <b>{time}</b>!",

    BonusReward.PENALTY_SNAP: "<tg-emoji emoji-id=\"5368469400695351161\">🐌</tg-emoji> Неудача! Щелчок недоступен ещё <b>{time}</b>.",
    BonusReward.PENALTY_COFFEE: "<tg-emoji emoji-id=\"5368469400695351161\">🐌</tg-emoji> Неудача! Кофе недоступен ещё <b>{time}</b>.",
    BonusReward.PENALTY_KAGUNE: "<tg-emoji emoji-id=\"5368469400695351161\">🐌</tg-emoji> Неудача! Кагуне недоступно ещё <b>{time}</b>.",

    BonusReward.SNAP_COUNT: "<tg-emoji emoji-id=\"5834596128246469018\">🫰</tg-emoji> +<b>{amount}</b> к щелчкам!",
    BonusReward.COFFEE_COUNT: "<tg-emoji emoji-id=\"5386470514871003633\">☕️</tg-emoji> +<b>{amount}</b> к выпитому кофе!",
    BonusReward.KAGUNE_LEVEL: "<tg-emoji emoji-id=\"5442804822048780010\">😫</tg-emoji> Кагуне выросло на <b>{amount}</b> ур.!",
    BonusReward.STAT_UP: "<tg-emoji emoji-id=\"5834929920219812289\">💪</tg-emoji> {stat} <b>+1</b>!",

    BonusReward.KAGUNE_DISCOUNT: "<tg-emoji emoji-id=\"5888620056551625531\">🏷</tg-emoji> Прокачка кагуне <b>−{percent}%</b> на <b>{time}</b>!",
    BonusReward.STATS_DISCOUNT: "<tg-emoji emoji-id=\"5888620056551625531\">🏷</tg-emoji> Прокачка статов <b>−{percent}%</b> на <b>{time}</b>!",
    BonusReward.KAGUNE_PRICE_UP: "<tg-emoji emoji-id=\"5875085613874548707\">📉</tg-emoji> Не повезло: прокачка кагуне <b>+{percent}%</b> на <b>{time}</b>.",
    BonusReward.STATS_PRICE_UP: "<tg-emoji emoji-id=\"5875085613874548707\">📉</tg-emoji> Не повезло: прокачка статов <b>+{percent}%</b> на <b>{time}</b>.",

    BonusReward.EMPTY: "<tg-emoji emoji-id=\"5834948255435198932\">🕳</tg-emoji> Коробка оказалась пустой… Повезёт завтра!",
}