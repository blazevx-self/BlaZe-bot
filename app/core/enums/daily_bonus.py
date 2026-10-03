from enum import StrEnum

class BonusReward(StrEnum):
    MONEY_SMALL = "money_small"
    MONEY_MEDIUM = "money_medium"
    MONEY_JACKPOT = "money_jackpot"
    MONEY_LOSS = "money_loss"

    QUIZ_QUESTIONS = "quiz_questions"
    QUIZ_RESET = "quiz_reset"
    QUIZ_REWARD_BOOST = "quiz_reward_boost"

    RESET_SNAP = "reset_snap"
    RESET_COFFEE = "reset_coffee"
    RESET_KAGUNE = "reset_kagune"
    RESET_ALL = "reset_all"

    FAST_SNAP = "fast_snap"
    FAST_COFFEE = "fast_coffee"
    FAST_KAGUNE = "fast_kagune"
    FAST_ALL = "fast_all"

    PENALTY_SNAP = "penalty_snap"
    PENALTY_COFFEE = "penalty_coffee"
    PENALTY_KAGUNE = "penalty_kagune"

    SNAP_COUNT = "snap_count"
    COFFEE_COUNT = "coffee_count"
    KAGUNE_LEVEL = "kagune_level"
    STAT_UP = "stat_up"

    KAGUNE_DISCOUNT = "kagune_discount"
    STATS_DISCOUNT = "stats_discount"
    KAGUNE_PRICE_UP = "kagune_price_up"
    STATS_PRICE_UP = "stats_price_up"

    EMPTY = "empty"

class EffectKey(StrEnum):
    SNAP_COOLDOWN = "snap_cooldown"
    COFFEE_COOLDOWN = "coffee_cooldown"
    KAGUNE_COOLDOWN = "kagune_cooldown"
    KAGUNE_PRICE = "kagune_price"
    STATS_PRICE = "stats_price"
    QUIZ_REWARD = "quiz_reward"