from typing import Any, Dict

def update_user(user: Dict[str, Any], **changes) -> Dict[str, Any]:
    """Обновляет локальные данные пользователя без изменения исходного словаря."""
    return {**user, **changes}