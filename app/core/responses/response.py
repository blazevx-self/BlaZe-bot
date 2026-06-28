def success(**kwargs):
    return {
        "success": True,
        **kwargs
    }

def error(**kwargs):
    return {
        "success": False,
        "show_alert": False,
        **kwargs
    }