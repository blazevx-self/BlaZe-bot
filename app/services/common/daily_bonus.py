import random
import time

from app.configs.game import game_cfg

from app.core.constants.game.daily_bonus import (
    R, ALL_REWARDS, GHOUL_REWARDS, KAGUNE_REWARDS,
    MONEY_RANGES, RESETS, PENALTIES, COUNTERS, EFFECTS,
    BONUS_TEXTS,
)
from app.core.constants.game.stats import STAT_LIMITS, STAT_NAMES
from app.core.enums import ResultStatus
from app.core.enums.cooldown_action import CooldownAction
from app.core.enums.daily_bonus import BonusReward, EffectKey

from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData
from app.types.services_result.common import DailyBonusResult

from app.services.cooldown import CooldownService

from app.database.models.common.user import UserOrm
from app.database.models.ghoul import GhoulOrm

from app.database.repositories.common.user import UserRepository
from app.database.repositories.ghoul import GhoulRepository
from app.database.repositories.game.quiz import QuizRepository

from app.utils.format_num import format_num
from app.utils.time import format_duration
from app.utils.logger import daily_bonus

class DailyBonusService:
    def __init__(
        self,
        user_repo: UserRepository,
        ghoul_repo: GhoulRepository,
        quiz_repo: QuizRepository,
        cooldown_service: CooldownService
    ):
        self.user_repo = user_repo
        self.ghoul_repo = ghoul_repo
        self.quiz_repo = quiz_repo
        self.cooldown_service = cooldown_service

    async def remaining(self, user: UserData) -> int:
        return await self.cooldown_service.remaining(
            telegram_id=user.telegram_id,
            action=CooldownAction.DAILY_BONUS
        )

    async def open_box(self, user: UserData, ghoul: GhoulData | None) -> DailyBonusResult:
        """Открывает коробку: ставит кулдаун, разыгрывает и выдаёт награду."""

        bonus_cfg = game_cfg.daily_bonus
        user_id = user.telegram_id

        claimed = await self.cooldown_service.claim(
            telegram_id=user_id,
            action=CooldownAction.DAILY_BONUS,
            duration=bonus_cfg.cooldown
        )

        if not claimed:
            return DailyBonusResult(
                status=ResultStatus.COOLDOWN,
                remaining=await self.remaining(user)
            )

        allowed = self._allowed_rewards(ghoul)

        reward = bonus_cfg.random_reward(allowed)
        others = [bonus_cfg.random_reward(allowed) for _ in range(bonus_cfg.boxes - 1)]

        values = await self._apply(reward, user, ghoul)

        daily_bonus.info(
            f"[BONUS] Opened | user_id={user_id} | reward={reward} | values={values}"
        )

        return DailyBonusResult(
            status=ResultStatus.SUCCESS,
            text=BONUS_TEXTS[reward].format(**values),
            reward=reward,
            others=others
        )

    @staticmethod
    def _allowed_rewards(ghoul: GhoulData | None) -> set[BonusReward]:
        allowed = set(ALL_REWARDS)

        if ghoul is None:
            allowed -= GHOUL_REWARDS

        if ghoul is None or not ghoul.kagune_was_obtained:
            allowed -= KAGUNE_REWARDS

        if ghoul is not None and not DailyBonusService._upgradable_stats(ghoul):
            allowed.discard(R.STAT_UP)

        return allowed

    @staticmethod
    def _upgradable_stats(ghoul: GhoulData) -> list[str]:
        return [stat for stat, limit in STAT_LIMITS.items() if getattr(ghoul, stat) < limit]

    async def _apply(self, reward: BonusReward, user: UserData, ghoul: GhoulData | None) -> dict:
        """Выдаёт награду и возвращает значения для текста."""

        bonus_cfg = game_cfg.daily_bonus
        user_id = user.telegram_id

        if reward in MONEY_RANGES:
            amount = random.randint(*getattr(bonus_cfg, MONEY_RANGES[reward]))
            user.money = await self.user_repo.change_money(user_id, amount)
            return {"amount": format_num(amount)}

        if reward == R.MONEY_LOSS:
            amount = min(random.randint(*bonus_cfg.money_loss), user.money)

            user.money = await self.user_repo.change_money(user_id, -amount)

            return {"amount": format_num(amount)}

        if reward == R.QUIZ_QUESTIONS:
            amount = random.randint(*bonus_cfg.quiz_questions)

            await self._refresh_quiz(user_id)

            await self.user_repo.change_data(
                user_id,
                quiz_questions_left=UserOrm.quiz_questions_left + amount
            )
            return {"amount": amount}

        if reward == R.QUIZ_RESET:
            await self._reset_quiz(user_id)
            return {}

        if reward in RESETS:
            for action in RESETS[reward]:
                await self.cooldown_service.reset(user_id, action)

            if reward == R.RESET_ALL:
                await self._reset_quiz(user_id)

            return {}

        if reward in PENALTIES:
            action = PENALTIES[reward]
            extra = random.randint(*bonus_cfg.penalty_duration)
            remaining = await self.cooldown_service.remaining(user_id, action)

            await self.cooldown_service.set(user_id, action, remaining + extra)

            return {"time": format_duration(extra, show_seconds=False)}

        if reward in COUNTERS:
            column, range_name = COUNTERS[reward]
            amount = random.randint(*getattr(bonus_cfg, range_name))

            await self.ghoul_repo.change_data(
                user_id,
                **{column: getattr(GhoulOrm, column) + amount}
            )

            return {"amount": amount}

        if reward == R.STAT_UP:
            stat = random.choice(self._upgradable_stats(ghoul))

            await self.ghoul_repo.change_data(user_id, **{stat: getattr(GhoulOrm, stat) + 1})
            return {"stat": STAT_NAMES[stat]}

        if reward in EFFECTS:
            keys, range_name = EFFECTS[reward]
            multiplier = round(random.uniform(*getattr(bonus_cfg, range_name)), 2)
            duration = random.randint(*bonus_cfg.effect_duration)

            await self._add_effects(user, keys, multiplier, duration)

            return {
                "percent": round(abs(1 - multiplier) * 100),
                "time": format_duration(duration, show_seconds=False)
            }

        return {} # EMPTY

    async def _refresh_quiz(self, user_id: int) -> None:
        """Обновляет дневной лимит викторины, чтобы бонус не затёрся сбросом в полночь."""

        await self.quiz_repo.get_quiz_access(
            telegram_id=user_id,
            daily_limit=game_cfg.quiz.day_limit
        )

    async def _reset_quiz(self, user_id: int) -> None:
        await self._refresh_quiz(user_id)
        await self.user_repo.change_data(
            user_id,
            quiz_questions_left=game_cfg.quiz.day_limit
        )

    async def _add_effects(
        self,
        user: UserData,
        keys: tuple[EffectKey, ...],
        multiplier: float,
        duration: int
    ) -> None:
        now = int(time.time())

        effects = {
            key: effect for key, effect in user.effects.items()
            if effect["until"] > 0
        }

        for key in keys:
            effects[key] = {"mult": multiplier, "until": now + duration}

        await self.user_repo.change_data(user.telegram_id, effects=effects)
        user.effects = effects