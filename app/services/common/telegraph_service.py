from telegraph import Telegraph

telegraph = Telegraph()
telegraph.create_account(short_name='BlaZe | Bot')

class TelegraphService:
    """Сервис создания страниц Telegraph."""

    @staticmethod
    def create_page(title: str, html: str) -> str:
        """Создаёт страницу Telegraph и возвращает ссылку на неё."""

        result = telegraph.create_page(
            title=title,
            html_content=html
        )

        return f"https://telegra.ph/{result['path']}"

telegraph_service = TelegraphService()