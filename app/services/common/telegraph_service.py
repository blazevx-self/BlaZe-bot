from telegraph import Telegraph

telegraph = Telegraph()
telegraph.create_account(short_name='BlaZe | Bot')

class TelegraphService:
    @staticmethod
    def create_page(title: str, html: str) -> str:
        r = telegraph.create_page(
            title=title,
            html_content=html
        )

        return "https://telegra.ph/" + r["path"]

telegraph_service = TelegraphService()