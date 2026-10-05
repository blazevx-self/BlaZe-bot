from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.database.models.media import MediaOrm
from app.database.repositories.base import Base

class MediaRepository(Base):
    async def get_file_id(self, path: str) -> str | None:
        stmt = select(MediaOrm.file_id).where(MediaOrm.path == path)
        return await self.session.scalar(stmt)

    async def save(self, path: str, file_id: str) -> None:
        stmt = (
            insert(MediaOrm)
            .values(path=path, file_id=file_id)
            .on_conflict_do_update(
                index_elements=[MediaOrm.path],
                set_={"file_id": file_id}
            )
        )

        await self.session.execute(stmt)