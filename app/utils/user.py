from typing import TypeVar
from typing import Any, Dict

T = TypeVar('T', bound=dict)

def update_user(user: Dict[str, Any], **changes) -> Dict[str, Any]:
    """Обновляет локальные данные пользователя без изменения исходного словаря."""
    return {**user, **changes}