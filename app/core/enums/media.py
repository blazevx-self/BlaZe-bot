from enum import StrEnum

class MediaKind(StrEnum):
    ANIMATION = "animation"
    VIDEO = "video"

class MediaCollection(StrEnum):
    """Значение = папка внутри app/assets/media."""

    SNAP = "snap"
    COFFEE = "coffee"
    EAT_HUMAN = "eat_human"

    KAGUNE_UKAKU = "kagune/ukaku"
    KAGUNE_KOUKAKU = "kagune/koukaku"
    KAGUNE_RINKAKU = "kagune/rinkaku"
    KAGUNE_BIKAKU = "kagune/bikaku"
    KAGUNE_OBTAINED = "kagune/obtained"

    EDITS = "edits"