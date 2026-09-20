from app.core.enums.rp_commands import TypeRpCommand
from app.types.services_result.rp_commands import RpCommandResult

from app.database.repositories.rp_commands_repository import RpCommandRepository

from app.utils.logger import rp_command_logger

_rp_cache: dict[int, dict[str, RpCommandResult]] = {}

class RpCommandService:
    def __init__(self, rp_repo: RpCommandRepository):
        self.rp_repo = rp_repo

    @staticmethod
    def _normalize_command(command: str) -> str:
        return command.strip().lower()

    @staticmethod
    def _to_entity(rp_command) -> RpCommandResult:
        return RpCommandResult(
            id=rp_command.id,
            command=rp_command.command,
            action=rp_command.action,
            type_command=rp_command.type_command,
            file_id=rp_command.file_id,
            created_at=rp_command.created_at
        )

    async def _load_cache(self, chat_id: int) -> None:
        rp_commands = await self.rp_repo.get_all(chat_id)

        _rp_cache[chat_id] = {c.command: self._to_entity(c) for c in rp_commands}
        rp_command_logger.info(f"[RP_COMMAND] Loaded {len(rp_commands)} RP commands | chat_id={chat_id}")

    async def get(self, chat_id: int, command: str) -> RpCommandResult | None:
        command = self._normalize_command(command)

        if chat_id not in _rp_cache:
            await self._load_cache(chat_id)

        return _rp_cache[chat_id].get(command)

    async def get_all(self, chat_id: int) -> list[RpCommandResult]:
        if chat_id not in _rp_cache:
            await self._load_cache(chat_id)

        return list(_rp_cache[chat_id].values())

    async def upsert(
        self,
        chat_id: int,
        command: str,
        action: str,
        type_command: TypeRpCommand,
        file_id: str | None = None
    ) -> RpCommandResult | None:
        command = self._normalize_command(command)

        if chat_id not in _rp_cache:
            await self._load_cache(chat_id)

        if len(_rp_cache[chat_id]) >= 20 and command not in _rp_cache[chat_id]:
            return None

        rp_command = await self.rp_repo.upsert(
            chat_id=chat_id,
            command=command,
            action=action,
            type_command=type_command,
            file_id=file_id
        )

        entity = self._to_entity(rp_command)

        _rp_cache.setdefault(chat_id, {})[command] = entity

        rp_command_logger.info(f"[RP_COMMAND] Upserted RP command={command} | chat_id={chat_id}")

        return entity

    async def delete(self, chat_id: int, command: str) -> bool:
        command = self._normalize_command(command)

        deleted = await self.rp_repo.delete(chat_id=chat_id, command=command)

        if not deleted:
            return False

        if chat_id in _rp_cache:
            _rp_cache[chat_id].pop(command, None)

        rp_command_logger.info(f"[RP_COMMAND] Deleted RP command={command} | chat_id={chat_id}")

        return True

    @staticmethod
    def clear_cache(chat_id: int) -> None:
        _rp_cache.pop(chat_id, None)
        rp_command_logger.info(f"[RP_COMMAND] Cleared RP command cache | chat_id={chat_id}")