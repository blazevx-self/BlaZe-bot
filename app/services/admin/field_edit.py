from app.core.constants.admin.fields import ALLOWED_USER_FIELDS, ALLOWED_GHOUL_FIELDS
from app.core.exceptions.user import UserNotFoundError

from app.types.services_result.admin import FieldEditResult

from app.database.repositories.user_repository import UserRepository
from app.database.repositories.ghoul_repository import GhoulRepository

from app.utils.logger import admin_logger

class FieldEditService:
    def __init__(self, user_repo: UserRepository, ghoul_repo: GhoulRepository):
        self.user_repo = user_repo
        self.ghoul_repo = ghoul_repo

    @staticmethod
    def _resolve_field(field: str) -> tuple[bool, bool]:
        if field in ALLOWED_USER_FIELDS:
            return True, False

        if field in ALLOWED_GHOUL_FIELDS:
            return True, True

        return False, False

    async def _resolve_user(self, query: str | int):
        user = await self.user_repo.resolve(query)

        if not user:
            raise UserNotFoundError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Пользователь не найден: {query}."
            )

        return user

    async def set_field(
        self,
        query: str | int,
        field: str,
        value: int,
        admin_id: int
    ) -> FieldEditResult:
        user = await self._resolve_user(query)

        is_valid, is_ghoul_valid = self._resolve_field(field)

        if not is_valid:
            raise ValueError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Неизвестное поле: {field}."
            )

        if not is_ghoul_valid:
            updated = await self.user_repo.change_data(user.telegram_id, **{field: value})

            return FieldEditResult(
                target=updated,
                field=field,
                value=value,
                is_ghoul_field=False
            )

        ghoul = await self.ghoul_repo.get(telegram_id=user.telegram_id)

        if not ghoul:
            raise ValueError(
                "<tg-emoji emoji-id=\"5386313314773002654ё\">⚠️</tg-emoji> "
                "У пользователя нет профиля гуля."
            )

        updated = await self.ghoul_repo.change_data(user.telegram_id,**{field: value})

        admin_logger.info(
            f"[SET_FIELD] Admin changed field | "
            f"admin_id={admin_id} | "
            f"user_id={user.telegram_id} | "
            f"field={field} | "
            f"value={value}"
        )

        return FieldEditResult(
            target=updated,
            field=field,
            value=value,
            is_ghoul_field=True
        )

    @staticmethod
    def fmt_operation_result(result: FieldEditResult) -> str:
        target = "гуля" if result.is_ghoul_field else "пользователя"
        return (
            "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji> "
            f"Поле <code>{result.field}</code> "
            f"{target} установлено в <code>{result.value}</code>."
        )

    @staticmethod
    def fmt_fields_help() -> str:
        return (
            "<tg-emoji emoji-id=\"5260399854500191689\">👤</tg-emoji> "
            f"<b>Поля пользователя:</b>\n<code>{', '.join(sorted(ALLOWED_USER_FIELDS))}</code>\n\n"
            "<tg-emoji emoji-id=\"5264782039697080626\">😒</tg-emoji> "
            f"<b>Поля гуля:</b>\n<code>{', '.join(sorted(ALLOWED_GHOUL_FIELDS))}</code>"
        )