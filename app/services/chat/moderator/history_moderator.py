from html import escape

from app.core.constants.chat.history_moderator import HISTORY_LIMIT, ACTION_ICONS

from app.types.services_result.chat import HistoryEntry, HistoryResult
from app.services.chat.moderator.moderation import ModerationService

from app.utils.truncate_text import truncate_text

class ChatHistoryService(ModerationService):
    async def history(self, chat_id: int, moderator_id: int, query: str | int) -> HistoryResult:
        await self._check_moderator(chat_id, moderator_id)

        target = await self._resolve_target(query)
        chat_pk = await self._get_chat(chat_id)

        rows = await self.moderator_action_repo.get_user_history(
            chat_id=chat_pk,
            user_id=target.id,
            limit=HISTORY_LIMIT
        )

        entries = [
            HistoryEntry(
                action=action.action,
                reason=action.reason,
                until=action.expires_at,
                created_at=action.created_at,
                moderator_name=moderator_name
            )
            for action, moderator_name in rows
        ]

        return HistoryResult(user=target, entries=entries)

    @staticmethod
    def fmt_history_result(result: HistoryResult) -> str:
        header = (
            "<tg-emoji emoji-id=\"5778299625370817409\">📋</tg-emoji> "
            f"<b>История</b> {escape(truncate_text(result.user.name))} "
            f"(<code>{result.user.telegram_id}</code>):\n\n"
        )

        if not result.entries:
            return header + "<i>Нарушений нет.</i>"

        lines = []

        for entry in result.entries:
            line = (
                f"{ACTION_ICONS.get(entry.action, '•')} "
                f"{entry.created_at.strftime('%d.%m %H:%M')} — <b>{entry.action}</b>"
            )

            if entry.until:
                line += f" до {entry.until.strftime('%d.%m %H:%M')}"

            if entry.reason:
                line += f" — <i>{escape(truncate_text(entry.reason, 40))}</i>"

            if entry.moderator_name:
                line += f" (модер: {escape(truncate_text(entry.moderator_name))})"

            lines.append(line)

        footer = (
            f"\n\n<i>Показаны последние {HISTORY_LIMIT}.</i>"
            if len(result.entries) == HISTORY_LIMIT
            else ""
        )

        return header + "\n".join(lines) + footer