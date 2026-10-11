from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from app.database.models.common.scheduled_notification import ScheduledNotificationOrm
from app.database.repositories.base import Base

class ScheduledNotificationRepository(Base):
    async def schedule(
            self,
            telegram_id: int,
            notification_type: str,
            fire_at: datetime,
            threshold: int | None = None
    ) -> None:
        stmt = (
            insert(ScheduledNotificationOrm)
            .values(
                telegram_id=telegram_id,
                notification_type=notification_type,
                threshold=threshold,
                fire_at=fire_at
            )
            .on_conflict_do_update(
                index_elements=["telegram_id", "notification_type"],
                set_={"threshold": threshold, "fire_at": fire_at}
            )
        )

        await self.session.execute(stmt)

    async def delete(self, telegram_id: int, notification_type: str) -> None:
        stmt = delete(ScheduledNotificationOrm).where(
            ScheduledNotificationOrm.telegram_id == telegram_id,
            ScheduledNotificationOrm.notification_type == notification_type
        )
        await self.session.execute(stmt)

    async def get_due(self, now: datetime) -> list[ScheduledNotificationOrm]:
        stmt = select(ScheduledNotificationOrm).where(
            ScheduledNotificationOrm.fire_at <= now
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())