def build_user_info(from_user, user_db=None) -> str:
    if isinstance(user_db, dict):
        return (
            f"name=\"{user_db.get('name', 'Unknown')}\" | "
            f"user_id={user_db.get('user_id', '?')}"
        )

    if from_user:
        return f"name=\"{from_user.first_name}\" | user_id={from_user.id}"

    return "Unknown"
