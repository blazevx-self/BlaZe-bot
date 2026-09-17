from datetime import datetime, timedelta, UTC

from app.configs.game import game_cfg
from app.configs.yaml_loader import cfg

from app.core.enums import ResultStatus
from app.core.exceptions.user import UserNotFoundError
from app.core.exceptions.transfer import (
    SelfTransferError,
    SenderTooNewError,
    InsufficientBalanceError,
    InvalidTransferAmountError,
    ReceiverLimitExceededError
)

from app.types.entities.user import UserData
from app.types.services_result.common import TransferResult

from app.database.repositories import UserRepository
from app.database.repositories.transfer_repository import TransferRepository

from app.utils.logger import transfer_logger
from app.utils.format_num import format_num

class TransferService:
    def __init__(
        self,
        user_repo: UserRepository,
        transfer_repo: TransferRepository,
    ):
        self.user_repo = user_repo
        self.transfer_repo = transfer_repo

    async def resolve_user(self, query: str | int) -> UserData:
        user = await self.user_repo.resolve(query)

        if not user:
            raise UserNotFoundError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Пользователь не найден: {query}."
            )

        return user

    async def validate(self, sender_id: int, receiver_id: int, amount: int) -> None:
        if amount < game_cfg.transfer.min_amount or amount > game_cfg.transfer.max_amount:
            raise InvalidTransferAmountError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Сумма перевода должна быть от "
                f"{game_cfg.transfer.min_amount} до "
                f"{game_cfg.transfer.max_amount}."
            )

        if sender_id == receiver_id:
            raise SelfTransferError(
               "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Нельзя перевести деньги самому себе."
            )

        sender = await self.user_repo.get(sender_id)

        if not sender:
            raise UserNotFoundError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Отправитель не найден."
            )

        receiver = await self.user_repo.get(receiver_id)

        if not receiver:
            raise UserNotFoundError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Получатель не найден."
            )

        account_age = datetime.now(UTC) - sender.created_at
        min_age = timedelta(days=game_cfg.transfer.min_sender_account_age_days)

        if account_age < min_age:
            raise SenderTooNewError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Переводы доступны после {game_cfg.transfer.min_sender_account_age_days} дней "
                "с момента регистрации."
            )

        if sender.money < amount:
            raise InsufficientBalanceError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Недостаточно денег для перевода."
            )

        received_last_24h = await self.transfer_repo.count_received_last_24h(
            receiver_id=receiver_id
        )

        if received_last_24h >= game_cfg.transfer.max_received_per_day:
            raise ReceiverLimitExceededError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Этот пользователь уже получил слишком много переводов за последние 24 часа."
            )

    async def transfer(self, sender_id: int, receiver_id: int, amount: int) -> TransferResult:
        await self.validate(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount
        )

        try:
            new_sender_balance = await self.user_repo.change_money(
                telegram_id=sender_id,
                amount=-amount
            )

            if new_sender_balance < 0:
                raise InsufficientBalanceError(
                    "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                    "Недостаточно денег для перевода."
                )

            new_receiver_balance = await self.user_repo.change_money(
                telegram_id=receiver_id,
                amount=amount
            )

            await self.transfer_repo.create_transfer(
                sender_id=sender_id,
                receiver_id=receiver_id,
                amount=amount
            )

        except Exception:
            transfer_logger.exception(
                f"[TRANSFER] Transfer failed | sender_id={sender_id} | "
                f"receiver_id={receiver_id} | amount={amount}"
            )
            raise

        transfer_logger.info(
            f"[TRANSFER] Transfer success | sender_id={sender_id} | receiver_id={receiver_id} | "
            f"amount={amount} | sender_balance={new_sender_balance} | receiver_balance={new_receiver_balance}"
        )

        text = cfg['message']['transfer']['translation'].format(
            amount=format_num(amount),
            receiver_id=receiver_id,
            new_sender_balance=format_num(new_sender_balance)
        )

        return TransferResult(
            status=ResultStatus.SUCCESS,
            text=text,
            amount=amount,
            receiver_id=receiver_id,
            sender_balance=new_sender_balance,
            receiver_balance=new_receiver_balance
        )