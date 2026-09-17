from app.database.models.user import UserOrm
from app.types.entities.user import UserData

def orm_to_user(user: UserOrm) -> UserData:
    return UserData(
        telegram_id=user.telegram_id,
        name=user.name,
        username=user.username,
    
        money=user.money,

        is_banned=user.is_banned,
        ban_reason=user.ban_reason,
        banned_until=user.banned_until,

        quiz_reset_date=user.quiz_reset_date,
        quiz_questions_left=user.quiz_questions_left,

        has_private_chat=user.has_private_chat,

        created_at=user.created_at
    )