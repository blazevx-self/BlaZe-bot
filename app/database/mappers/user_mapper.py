from app.types.entities import UserData
from typing import Any, Mapping


def row_to_user(row: Mapping[str, Any]) -> UserData:

    return UserData(
        user_id=row["user_id"],
        name=row["name"],
        username=row["username"],
        money=row["money"],
        is_subscribed=bool(row["is_subscribed"]),

        kagune_was_obtained=bool(row["kagune_was_obtained"]),
        kagune_lvl=row["kagune_lvl"],
        kagune_type=row["kagune_type"],
        kagune_last_grow=row["kagune_last_grow"],
        kakuja_activated=bool(row["kakuja_activated"]) if "kakuja_activated" in row.keys() else False,

        strength=row["strength"],
        agility=row["agility"],
        speed=row["speed"],
        hp=row["hp"],
        regen=row["regen"],

        level=row["level"],

        last_snap=row["last_click"],
        snap=row["clicks"],

        coffee_last_time=row["coffee_last_time"],
        coffee_cooldown=row["coffee_cooldown"],
        coffee_total=row["coffee_total"],
    )