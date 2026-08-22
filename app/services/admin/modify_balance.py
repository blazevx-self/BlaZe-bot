from app.core.constants.admin.modify_balance import MAX_AMOUNT

from app.types.entities import UserData
from app.types.services_result.admin import ModifyBalanceResult

from app.database.repositories.users_repository import user_repository
from app.utils.format_num import format_num

class ModifyBalanceService:
    @staticmethod
    async def _resolve_user(query: str | int) -> UserData:
        user = await user_repository.resolve(query)

        if not user:
            raise ValueError(f"⚠️ Пользователь не найден: {query}")

        return user
    
    
    async def modify_balance(self, query: str | int, amount: int) -> ModifyBalanceResult:
        if amount == 0:
            raise ValueError("⚠️ Сумма операции не может быть равна 0.")

        if abs(amount) > MAX_AMOUNT:
            raise ValueError(f"⚠️ Превышен лимит суммы операции ({format_num(MAX_AMOUNT)} BC).")
        
        user = await self._resolve_user(query)
        new_balance = await user_repository.modify_balance(user_id=user.user_id, amount=amount)
        
        return ModifyBalanceResult(
            user=user,
            amount=amount,
            balance=new_balance
        )


    @staticmethod
    def fmt_operation_result(result: ModifyBalanceResult) -> str:
        action = "начислено" if result.amount > 0 else "списано"
        return (
            f"✅ Пользователю <code>{result.user.user_id}</code> "
            f"({result.user.name}) {action} "
            f"<b>{format_num(abs(result.amount))} BlaZeCoin.</b>"
        )
        
balance_service = ModifyBalanceService()
