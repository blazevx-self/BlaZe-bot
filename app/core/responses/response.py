def success(**kwargs) -> dict:
    return {
        "success": True,
        **kwargs
    }

def error(
        *,
        notification=None,
        show_alert=False,
        reason=None,
        **kwargs
) -> dict:
    result = {
        "success": False,
        "show_alert": show_alert
    }

    if notification is not None:
        result["notification"] = notification

    if reason is not None:
        result["reason"] = reason

    result.update(kwargs)

    return result