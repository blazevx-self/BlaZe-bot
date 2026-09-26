from html import escape

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner, User

from app.utils.truncate_text import truncate_text

class ListAdminsService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def get_admins(
        self,
        chat_id: int
    ) -> tuple[ChatMemberOwner | None, list[ChatMemberAdministrator]]:
        members = await self.bot.get_chat_administrators(chat_id)

        visible = [m for m in members if not m.user.is_bot and not m.is_anonymous]

        owner = next((m for m in visible if m.status == ChatMemberStatus.CREATOR), None)
        admins = [m for m in visible if m.status == ChatMemberStatus.ADMINISTRATOR]

        return owner, admins

    @staticmethod
    def _link(user: User) -> str:
        """Ссылка без пинга: ник -> t.me, без ника -> просто имя."""

        name = escape(truncate_text(user.full_name))

        if user.username:
            return f"<a href=\"https://t.me/{user.username}\">{name}</a>"

        return name


    def fmt_admins(
        self,
        owner: ChatMemberOwner | None,
        admins: list[ChatMemberAdministrator]
    ) -> str:
        text = "<tg-emoji emoji-id=\"6032693626394382504\">👤</tg-emoji> <b>Администрация чата</b>\n\n"

        if owner:
            title = f" — <i>{escape(owner.custom_title)}</i>" if owner.custom_title else ""
            text += (
                "<tg-emoji emoji-id=\"5805553606635559688\">👑</tg-emoji> "
                f"<b>Создатель:</b> {self._link(owner.user)}{title}\n\n"
            )

        if admins:
            text += (
                "<tg-emoji emoji-id=\"6030445631921721471\">🛡</tg-emoji>"
                f"<b>Администраторы ({len(admins)}):</b>\n"
            )

            for admin in admins:
                title = f" — <i>{escape(admin.custom_title)}</i>" if admin.custom_title else ""
                text += f"└ {self._link(admin.user)}{title}\n"

        if not owner and not admins:
            text += "<i>Администраторы скрыты.</i>"

        return text