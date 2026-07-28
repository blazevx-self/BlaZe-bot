def truncate_text(text: str, limit: int=12) -> str:
    """Обрезает длинный текст до limit символов.
       Если текст длиннее - добавляет "...".

       Examples:
           "VeryLongNickname" -> "VeryLongN..."
           "Blaze" -> "Blaze"
    """

    if len(text) <= limit:
        return text

    return text[:limit - 3] + "..."
