from typing import Any, Dict

def update_user(user: Dict[str, Any], **changes) -> Dict[str, Any]:
    return {**user, **changes}