from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

from app.database.repositories.base import Base
from app.database.models.rp_commands import RpCommandOrm

from app.core.enums.rp_commands import TypeRpCommand

class RpCommandRepository(Base):
    async def get(self, chat_id: int, command: str) -> RpCommandOrm | None:
        stmt = select(RpCommandOrm).where(
            RpCommandOrm.chat_id == chat_id,
            RpCommandOrm.command == command
        )
        return await self.session.scalar(stmt)

    async def get_all(self, chat_id: int) -> list[RpCommandOrm]:
        stmt = (
            select(RpCommandOrm)
            .where(RpCommandOrm.chat_id == chat_id)
            .order_by(RpCommandOrm.command.asc())
        )

        result = await self.session.scalars(stmt)

        return list(result)

    async def upsert(
        self,
        chat_id: int,
        command: str,
        action: str,
        type_command: TypeRpCommand,
        file_id: str | None = None
    ) -> RpCommandOrm:
        stmt = (
            insert(RpCommandOrm)
            .values(
                chat_id=chat_id,
                command=command,
                action=action,
                type_command=type_command,
                file_id=file_id
            )
            .on_conflict_do_update(
                index_elements=[
                    "chat_id",
                    "command"
                ],
                set_={
                    "action": action,
                    "type_command": type_command,
                    "file_id": file_id
                }
            )
            .returning(RpCommandOrm)
        )

        rp_command = await self.session.scalar(stmt)

        if rp_command is None:
            raise RuntimeError("Failed to save RP-command.")

        return rp_command

    async def delete(self, chat_id: int, command: str) -> bool:
        stmt = (
            delete(RpCommandOrm)
            .where(
                RpCommandOrm.chat_id == chat_id,
                RpCommandOrm.command == command
            )
            .returning(RpCommandOrm)
        )

        deleted_id = await self.session.scalar(stmt)

        return deleted_id is not None
