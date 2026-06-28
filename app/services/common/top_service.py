from app.database.repositories.users_repository import user_repository

# noinspection PyMethodMayBeStatic
class TopService:
    async def process_top(self, user: dict):
        return {
            "top_users": await user_repository.get_user_top(15),
            "rank": await user_repository.get_user_rank(user["user_id"]),
            "user": user
        }

top_service = TopService()