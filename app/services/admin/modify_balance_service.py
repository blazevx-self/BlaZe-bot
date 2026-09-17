from app.core.constants.admin.modify_balance import MAX_AMOUNT
from app.core.exceptions.user import UserNotFoundError

from app.types.services_result.admin import ModifyBalanceResult
from app.types.entities.user import UserData

from app.database.repositories.user_repository import UserRepository

from app.utils.logger import admin_logger
from app.utils.format_num import format_num

class ModifyBalanceService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def _resolve_user(self, query: str | int) -> UserData:
        user = await self.user_repo.resolve(query)

        if not user:
            raise UserNotFoundError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Пользователь не найден: {query}.")

        return user

    async def modify_balance(self, query: str | int, amount: int, admin_id: int) -> ModifyBalanceResult:
        if amount == 0:
            raise ValueError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Сумма операции не может быть равна 0."
            )

        if abs(amount) > MAX_AMOUNT:
            raise ValueError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Превышен лимит суммы операции ({format_num(MAX_AMOUNT)} BC)."
            )

        if amount < 0:
            raise ValueError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Сумма операции не может быть меньше 0."
            )

        user = await self._resolve_user(query)
        balance = await self.user_repo.change_money(telegram_id=user.telegram_id, amount=amount)

        admin_logger.info(
            f"[MODIFY_BALANCE] Balance changed | "
            f"admin_id={admin_id} | "
            f"user_id={user.telegram_id} | "
            f"amount={amount} | "
            f"new_balance={balance}"
        )

        return ModifyBalanceResult(
            user=user,
            amount=amount,
            balance=balance
        )

    @staticmethod
    def fmt_operation_result(result: ModifyBalanceResult) -> str:
        action = "начислено" if result.amount > 0 else "списано"
        return (
            "<tg-emoji emoji-id=\"5260416304224936047\">✅</tg-emoji>"
            f"Пользователю <code>{result.user.telegram_id}</code> "
            f"({result.user.name}) {action} "
            f"<b>{format_num(abs(result.amount))} BlaZeCoin.</b>"
        )