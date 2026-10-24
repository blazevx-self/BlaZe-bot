import html

from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.types import Message

from dependency_injector.wiring import Provide, inject
from app.containers import Container

from app.database.repositories.common.user import UserRepository

from app.services.common.family import FamilyService
from app.bot.filters.group_only import GroupOnlyFilter

from app.utils.time import format_duration

from .helpers import FAM, _mention

router = Router()

def _together(created_at: datetime) -> tuple[str, str]:
    since = created_at.strftime("%d.%m.%Y")
    start = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)

    age = format_duration(int((datetime.now(timezone.utc) - start).total_seconds()), show_seconds=False)
    return since, age

@router.message(F.text.lower() == "браки", GroupOnlyFilter())
@inject
async def families_cmd(
    message: Message,
    family_service: FamilyService = Provide[Container.family_service],
    user_repo: UserRepository = Provide[Container.user_repo],
) -> None:
    families = await family_service.families_in_chat(message.chat.id)

    if not families:
        await message.reply(FAM["list_empty"])
        return

    rows = []

    for i, fam in enumerate(families, start=1):
        members = []

        for m in await family_service.family_repo.list_members(fam.id):
            u = await user_repo.get_by_id(m.user_id)
            if u is not None:
                members.append(_mention(u))

        names = ", ".join(members) if members else "—"
        since, age = _together(fam.created_at)

        if fam.name:
            rows.append(FAM["list_named"].format(
                place=i, name=html.escape(fam.name),
                members=names, since=since, age=age
            ))
        else:
            rows.append(FAM["list_row"].format(
                place=i, members=names,
                since=since, age=age,
            ))

    await message.reply(FAM["list"].format(count=len(families), rows="\n".join(rows)))