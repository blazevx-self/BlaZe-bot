from datetime import datetime, timedelta, UTC

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert

from app.database.repositories.base import Base
from app.database.models.transfer import TransferOrm

class TransferRepository(Base):
    async def create_transfer(
        self,
        sender_id: int,
        receiver_id: int,
        amount: int
    ) -> TransferOrm:
        stmt = (
            insert(TransferOrm)
            .values(
                sender_id=sender_id,
                receiver_id=receiver_id,
                amount=amount
            )
            .returning(TransferOrm)
        )

        transfer = await self.session.scalar(stmt)

        if transfer is None:
            raise ValueError("Transfer was not created")

        return transfer

    async def count_received_since(self, receiver_id: int, since: datetime) -> int:
        stmt = (
            select(func.count())
            .select_from(TransferOrm)
            .where(
                TransferOrm.receiver_id == receiver_id,
                TransferOrm.created_at >= since
            )
        )

        count = await self.session.scalar(stmt)

        return int(count or 0)

    async def count_received_last_24h(self, receiver_id: int) -> int:
        since = datetime.now(UTC) - timedelta(hours=24)
        return await self.count_received_since(receiver_id=receiver_id, since=since)