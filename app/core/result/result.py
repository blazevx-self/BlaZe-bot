from app.core.enums import ResultStatus

def result(status: ResultStatus, **kwargs) -> dict:
    """Унифицированный результат для всех сервисов."""
    return {"status": status, **kwargs}