from html import escape
from datetime import datetime, UTC

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from app.configs.yaml_loader import cfg

from app.database.repositories.common.user import UserRepository
from app.database.repositories.chat.chat_member import ChatMemberRepository

from app.utils.logger import system_logger
from app.utils.truncate_text import truncate_text

class BirthdayService:
    def __init__(
        self,
        bot: Bot,
        user_repo: UserRepository,
        chat_member_repo: ChatMemberRepository
    ):
        self.bot = bot
        self.user_repo = user_repo
        self.chat_member_repo = chat_member_repo

    @staticmethod
    def parse_date(value: str) -> tuple[int, int, int | None] | None:
        raw = value.strip()
        parts = raw.split('.')

        try:
            if len(parts) == 2:
                date = datetime.strptime(f"{raw}.2000", "%d.%m.%Y")
                return date.day, date.month, None

            if len(parts) == 3:
                date = datetime.strptime(raw, "%d.%m.%Y")
                year = date.year
                now_year = datetime.now(UTC).year

                if year < 1920 or year > now_year:
                    return None

                return date.day, date.month, year
        except ValueError:
            return None

        return None

    async def set_birthday(
        self,
        telegram_id: int,
        value: str,
    ) -> tuple[int, int, int | None] | None:
        parsed = self.parse_date(value)

        if parsed:
            day, month, year = parsed
            await self.user_repo.set_birthday(telegram_id, day, month, year)

        return parsed

    async def remove_birthday(self, telegram_id: int) -> None:
        await self.user_repo.set_birthday(telegram_id, None, None, None)

    async def congratulate(self, day: int, month: int) -> None:
        texts = cfg["message"]["birthday"]
        birthdays = await self.user_repo.get_birthdays(day, month)

        for chat_id, names in birthdays.items():
            people = ", ".join(
                f"<b>{escape(truncate_text(name))}</b>" for name in names
            )

            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=texts["chat"].format(people=people)
                )
            except TelegramAPIError as e:
                system_logger.warning(
                    f"[BIRTHDAY] Chat send failed | chat_id={chat_id} | {e}"
                )

        users = await self.user_repo.get_birthdays(day, month)

        for telegram_id, name in users:
            try:
                await self.bot.send_message(
                    chat_id=telegram_id,
                    text=texts["pm"].format(name=escape(truncate_text(name)))
                )
            except TelegramAPIError as e:
                system_logger.warning(
                    f"[BIRTHDAY] PM send failed | user_id={telegram_id} | {e}"
                )