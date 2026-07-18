from app.types.entities import UserData

def build_user_info(from_user, user_db=None) -> str:
    """
    Единый формат user_info для логов.

    Позволяет:
    - избежать дублирования форматирования в middleware/сервисах
    - поддерживать единый стиль логов
    - скрывать внутреннюю структуру user объекта
    """
    if isinstance(user_db, UserData):
        return (
            f"name=\"{user_db.name}\" | "
            f"user_id={user_db.user_id}"
        )

    if from_user is not None:
        return f"name=\"{from_user.first_name}\" | user_id={from_user.id}"

    return "Unknown"
