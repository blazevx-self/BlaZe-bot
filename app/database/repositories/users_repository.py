from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.database.models.user import UserOrm
from app.database.repositories.base import Base

from app.utils.logger import system_logger

class UserRepository(Base):
    async def upsert(
        self,
        telegram_id: int,
        name: str,
        username: str | None = None,
    ) -> UserOrm:
        system_logger.debug(f"[DB] Upserting user: telegram_id={telegram_id} | name={name} | username={username}")
        
        stmt = (
            insert(UserOrm)
            .values(
                telegram_id=telegram_id,
                name=name,
                username=username
            )
            .on_conflict_do_update(
                index_elements=[UserOrm.telegram_id],
                set_={
                    "name": name,
                    "username": username
                }
            )
            .returning(UserOrm)
        )

        user = await self.session.scalar(stmt)
        
        if user is None:
            system_logger.error(f"[DB] User ({telegram_id}) not found after UPSERT")
            raise ValueError(f"User ({telegram_id}) not found after UPSERT")

        system_logger.debug(f"[DB] User upserted successfully: id={user.id}")

        return user
    

    async def get(self, search_parameter: int | str) -> UserOrm:
        system_logger.debug(f"[DB] Get user | search_parameter={search_parameter}")

        if isinstance(search_parameter, int):
            search_column = UserOrm.telegram_id
            search_type = "telegram_id"
        else:
            search_column = UserOrm.username
            search_type = "username"
            search_parameter = search_parameter.lstrip("@")

        stmt = select(UserOrm).where(search_column == search_parameter)

        user = await self.session.scalar(stmt)

        if user is None:
            system_logger.debug(f"[DB] User not found | {search_type}={search_parameter}")
            return None

        system_logger.debug(f"[DB] User found | id={user.id}")

        return user
    

    async def activate_subscribed_bonus(self, telegram_id: int, bonus: int) -> UserOrm:
        stmt = (
            update(UserOrm)
            .where(UserOrm.telegram_id == telegram_id)
            .values(
                money=UserOrm.money + bonus,
                is_subscribed=True
            )
            .returning(UserOrm)
        )

        user = await self.session.scalar(stmt)

        if user is None:
            raise ValueError(f"User ({telegram_id}) not found")

        return user
    

    async def change_money(self, telegram_id: int, amount: int) -> UserOrm:
        stmt = (
            update(UserOrm)
            .where(UserOrm.telegram_id == telegram_id)
            .values(money=UserOrm.money + amount)
            .returning(UserOrm)
        )
        
        user = await self.session.scalar(stmt)
        
        if user is None:
            raise ValueError(f"User ({telegram_id}) not found")
        
        return user


    async def change_data(self, telegram_id: int, **kwargs) -> UserOrm:
        if not kwargs:
            raise ValueError("No fields to update")
        
        stmt = (
            update(UserOrm)
            .where(UserOrm.telegram_id == telegram_id)
            .values(**kwargs)
            .returning(UserOrm)
        )

        user = await self.session.scalar(stmt)

        if user is None:
            raise ValueError(f"User ({telegram_id}) not found")

        return user


    async def ban(
        self,
        telegram_id: int,
        reason: str | None = None,
        banned_until: datetime | None = None,
    ) -> UserOrm:
        return await self.change_data(
            telegram_id,
            is_banned=True,
            ban_reason=reason,
            banned_until=banned_until,
        )


    async def unban(self, telegram_id: int) -> UserOrm:
        return await self.change_data(
            telegram_id,
            is_banned=False,
            ban_reason=None,
            banned_until=None,
        )
        

    async def get_top_balance(self, telegram_id: int, )