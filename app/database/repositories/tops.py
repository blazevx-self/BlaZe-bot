from sqlalchemy import select, func

from app.database.repositories.base import Base
from app.database.repositories.common.family import FamilyOrm, FamilyMemberOrm
from app.database.models.common.user import UserOrm
from app.database.models.ghoul.ghoul import GhoulOrm
from app.database.mappers.user import orm_to_user
from app.database.mappers.ghoul import orm_to_ghoul

from app.types.services_result.tops import TopUser

class TopsRepository(Base):
    async def get_top(self, top_type: str, limit: int) -> list[TopUser]:
        if top_type == "money":
            return await self._top_money(limit)

        elif top_type == "snap":
            value_column = GhoulOrm.snap_count

        elif top_type == "kagune":
            value_column = GhoulOrm.kagune_strength

        elif top_type == "coffee":
            value_column = GhoulOrm.coffee_count

        else:
            raise ValueError(f"Unknown top type: {top_type}")

        stmt = (
            select(UserOrm, GhoulOrm)
            .outerjoin(
                GhoulOrm,
                GhoulOrm.telegram_id == UserOrm.telegram_id
            )
            .where(value_column > 0)
            .order_by(value_column.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return [
            TopUser(
                user=orm_to_user(user),
                ghoul=orm_to_ghoul(ghoul) if ghoul else None
            )
            for user, ghoul in result.all()
        ]

    async def get_rank(self, telegram_id: int, top_type: str) -> int | None:
        if top_type == "money":
            value = await self.get_display_money(telegram_id)

            if value <= 0:
                return None

            member_ids = select(FamilyMemberOrm.user_id)

            singles_above = await self.session.scalar(
                select(func.count()).select_from(UserOrm).where(
                    UserOrm.money > value,
                    UserOrm.id.not_in(member_ids),
                )
            ) or 0

            fam_above = await self.session.scalar(
                select(func.count()).select_from(FamilyOrm).where(
                    FamilyOrm.dissolved_at.is_(None),
                    FamilyOrm.money > value,
                )
            ) or 0

            return singles_above + fam_above + 1

        elif top_type == "snap":
           model = GhoulOrm
           value_column = GhoulOrm.snap_count

        elif top_type == "kagune":
            model = GhoulOrm
            value_column = GhoulOrm.kagune_strength

        elif top_type == "coffee":
            model = GhoulOrm
            value_column = GhoulOrm.coffee_count

        else:
            raise ValueError(f"Unknown top type: {top_type}")
        
        rank = func.rank().over(order_by=value_column.desc()).label("rank")
        
        ranked = (
            select(
                model.telegram_id,
                rank
            )
            .where(value_column > 0)
            .subquery()
        )
        
        stmt = select(ranked.c.rank).where(ranked.c.telegram_id == telegram_id)
        
        return await self.session.scalar(stmt)

    async def get_display_money(self, telegram_id: int) -> int:
        user = await self.session.scalar(
            select(UserOrm).where(UserOrm.telegram_id == telegram_id)
        )

        if user is None:
            return 0

        family_id = await self.session.scalar(
            select(FamilyMemberOrm.family_id).where(FamilyMemberOrm.user_id == user.id)
        )

        if family_id is None:
            return user.money

        money = await self.session.scalar(
            select(FamilyOrm.money).where(FamilyOrm.id == family_id)
        )

        return money or 0

    async def _top_money(self, limit: int) -> list[TopUser]:
        member_ids = select(FamilyMemberOrm.user_id)

        singles = list((await self.session.scalars(
            select(UserOrm).where(
                UserOrm.money > 0,
                UserOrm.id.not_in(member_ids),
            )
        )).all())

        families = list((await self.session.scalars(
            select(FamilyOrm).where(
                FamilyOrm.dissolved_at.is_(None),
                FamilyOrm.money > 0,
            )
        )).all())

        rows: list[tuple[int, TopUser]] = []

        for u in singles:
            rows.append((u.money, TopUser(user=orm_to_user(u), money=u.money)))

        for fam in families:
            members = list((await self.session.scalars(
                select(FamilyMemberOrm).where(FamilyMemberOrm.family_id == fam.id)
            )).all())

            people = []

            for m in members:
                u = await self.session.get(UserOrm, m.user_id)

                if u is not None:
                    people.append(u)

            if not people:
                continue

            partner = orm_to_user(people[1]) if len(people) > 1 else None

            rows.append((
                fam.money,
                TopUser(user=orm_to_user(people[0]), partner=partner, money=fam.money),
            ))

        rows.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in rows[:limit]]