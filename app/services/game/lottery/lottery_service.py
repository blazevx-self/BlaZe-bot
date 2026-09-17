import asyncio

from app.configs.game import game_cfg
from app.configs.yaml_loader import cfg

from app.core.enums.lottery import LotteryColor

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData
from app.types.services_result.game import LotteryResult

from app.database.repositories.user_repository import UserRepository
from app.database.repositories.lottery_repository import LotteryRepository

from app.services.game.lottery.lottery_video_generator import LotteryVideoGenerator

from app.utils.logger import lottery_logger
from app.utils.format_num import format_num

class LotteryService:
    def __init__(
        self,
        user_repo: UserRepository,
        lottery_repo: LotteryRepository,
        video_generator: LotteryVideoGenerator,
    ):
        self.user_repo = user_repo
        self.lottery_repo = lottery_repo
        self.video_generator = video_generator

    @staticmethod
    def _validate_bet(bet_amount: int) -> None:
        if not (
            game_cfg.lottery.min_bet
            <= bet_amount
            <= game_cfg.lottery.max_bet
        ):
            raise ValueError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                f"Сумма ставки должна быть от "
                f"<b>{game_cfg.lottery.min_bet}</b> до "
                f"<b>{game_cfg.lottery.max_bet}</b>."
            )

    @staticmethod
    def parse_color(color_str: str) -> LotteryColor:
        """Преобразует строку в цвет лотереи"""

        color_str = color_str.lower().strip().replace("ё", "е")

        for color in LotteryColor:
            if color.value.replace("ё", "е") in color_str:
                return color

        raise ValueError(
            "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
            f"Неизвестный цвет <b>«{color_str}».</b> \n\n"
            "<tg-emoji emoji-id=\"5258503720928288433\">ℹ️</tg-emoji> "
            f"<b>Используйте:</b> \n{', '.join(c.value for c in LotteryColor)}"
        )

    async def execute(
        self,
        user: UserData,
        ghoul: GhoulData,
        chosen_color: LotteryColor,
        bet_amount: int
    ) -> LotteryResult:
        """Выполняет ставку и определяет результат"""

        user_id = user.telegram_id

        self._validate_bet(bet_amount)

        if user.money < bet_amount:
            raise ValueError(
                "<tg-emoji emoji-id=\"5386313314773002654\">⚠️</tg-emoji> "
                "Недостаточно денег для такой ставки."
            )

        winning_color = game_cfg.lottery.get_random_color()
        is_won = chosen_color == winning_color

        if is_won:
            multiplier = game_cfg.lottery.get_multiplier(winning_color)
            payout = int(bet_amount * multiplier)
            earned = payout - bet_amount
        else:
            multiplier = None
            earned = -bet_amount

        video = await asyncio.to_thread(
            self.video_generator.generate,
            winning_color
        )

        try:
            new_balance = await self.user_repo.change_money(
                telegram_id=user_id,
                amount=earned,
            )

            await self.lottery_repo.insert(
                telegram_id=user_id,
                bet_amount=bet_amount,
                chosen_color=chosen_color.value,
                winning_color=winning_color.value,
                is_won=is_won,
                earned=earned
            )

        except Exception:
            lottery_logger.exception(f"[LOTTERY] Dep failed | user_id={user_id} | bet_amount={bet_amount}")
            raise

        user.money = new_balance

        lottery_logger.info(
            f"[LOTTERY] Dep result | user_id={user_id} | "
            f"chosen_color={chosen_color.value} | winning_color={winning_color.value} | "
            f"bet_amount={bet_amount} | earned={earned} | balance={new_balance}"
        )

        if is_won:
            text = cfg["message"]["lottery"]["win"].format(
                chosen_color=chosen_color.value,
                winning_color=winning_color.value,
                bet=format_num(bet_amount),
                earned=format_num(earned),
                multiplier=multiplier,
                money=format_num(new_balance),
            )
        else:
            text = cfg["message"]["lottery"]["lose"].format(
                chosen_color=chosen_color.value,
                winning_color=winning_color.value,
                bet=format_num(bet_amount),
                money=format_num(new_balance),
            )

        return LotteryResult(
            user=user,
            ghoul=ghoul,
            bet_amount=bet_amount,
            chosen_color=chosen_color,
            winning_color=winning_color,
            is_won=is_won,
            earned=earned,
            video=video,
            text=text
        )