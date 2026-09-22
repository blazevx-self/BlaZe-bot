from telegraph import Telegraph

from app.configs.settings import settings
from app.core.templates.common.telegraphpy import build_help_telegraph

class TelegraphService:
    def __init__(self):
        self.telegraph = Telegraph(access_token=settings.TELEGRAPH_ACCESS_TOKEN.get_secret_value())

    def update_page(self) -> None:
        self.telegraph.edit_page(
            path=settings.TELEGRAPH_PAGE_PATH,
            title="BlaZe | Bot — Помощь",
            html_content=build_help_telegraph(),
        )

    @property
    def url(self) -> str:
        return f"https://telegra.ph/{settings.TELEGRAPH_PAGE_PATH}"