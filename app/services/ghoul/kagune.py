from app.configs.game import game_cfg
from app.configs.yaml_loader import cfg

from app.core.enums import ResultStatus
from app.core.enums.cooldown_action import CooldownAction
from app.core.enums.daily_bonus import EffectKey
from app.core.enums.media import MediaCollection
from app.core.exceptions.ghoul import KaguneInitializationError

from app.types.services_result.ghoul import KaguneResult
from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.database.repositories.ghoul.ghoul import GhoulRepository
from app.database.repositories.common.user import UserRepository

from app.services.ghoul.ghoul import GhoulService
from app.services.cooldown import CooldownService
from app.services.ghoul.hunger.hunger import HungerService
from app.services.common.family import FamilyService

from app.utils.format_num import format_num
from app.utils.logger import kagune_logger
from app.utils.effects import apply_effect

class KaguneService:
    def __init__(
        self,
        ghoul_repo: GhoulRepository,
        user_repo: UserRepository,
        ghoul_service: GhoulService,
        cooldown_service: CooldownService,
        hunger_service: HungerService,
        family_service: FamilyService
    ):
        self.ghoul_repo = ghoul_repo
        self.user_repo = user_repo
        self.ghoul_service = ghoul_service
        self.cooldown_service = cooldown_service
        self.hunger_service = hunger_service
        self.family_service = family_service

    async def obtaining_kagune(self, user: UserData, ghoul: GhoulData | None) -> KaguneResult:
        user_id = user.telegram_id

        if ghoul is not None and ghoul.is_dead:
            kagune_type = game_cfg.kagune.random_type()

            await self.ghoul_service.reset_for_rebirth(user_id, kagune_type)
            await self.hunger_service.schedule_for(user_id)

            return KaguneResult(
                status=ResultStatus.SUCCESS,
                kagune_type=kagune_type,
                collection=MediaCollection.KAGUNE_OBTAINED,
            )

        if ghoul is not None and ghoul.kagune_was_obtained:
            return KaguneResult(status=ResultStatus.ALREADY_GHOUL)

        kagune_type = game_cfg.kagune.random_type()

        if ghoul is None:
            await self.ghoul_repo.upsert(
                telegram_id=user_id,
                kagune_type=kagune_type
            )

        try:
            await self.ghoul_repo.init_kagune(
                telegram_id=user_id,
                kagune_type=kagune_type
            )
        except KaguneInitializationError:
            kagune_logger.warning(f"[KAGUNE] Initialization failed | user_id={user_id}")
            return KaguneResult(status=ResultStatus.ERROR)

        kagune_logger.info(f"[KAGUNE] First kagune obtained | user_id={user_id} | type={kagune_type}")

        await self.hunger_service.schedule_for(user_id)

        return KaguneResult(
            status=ResultStatus.SUCCESS,
            kagune_type=kagune_type,
            collection=MediaCollection.KAGUNE_OBTAINED
        )

    async def upgrade_kagune(self, user: UserData, ghoul: GhoulData) -> KaguneResult:
        user_id = user.telegram_id

        if ghoul and ghoul.is_dead:
            return KaguneResult(status=ResultStatus.NO_KAGUNE)

        if not ghoul or not ghoul.kagune_was_obtained:
            kagune_logger.debug(f"[KAGUNE] Upgrade denied | user_id={user_id} | reason=no_kagune")
            return KaguneResult(status=ResultStatus.NO_KAGUNE)

        remaining = await self.cooldown_service.remaining(
            telegram_id=user_id,
            action=CooldownAction.KAGUNE_GROW
        )

        # ограничение скорости прокачки (ап раз в 15 минут)
        if remaining > 0:
            return KaguneResult(
                status=ResultStatus.COOLDOWN,
                remaining=remaining
            )

        level = ghoul.kagune_strength
        price = apply_effect(user, EffectKey.KAGUNE_PRICE, self.ghoul_service.get_price_kagune(level))

        wallet = await self.family_service.balance_of(user_id)

        # проверка баланса перед апом
        if wallet < price:
            return KaguneResult(
                status=ResultStatus.NOT_ENOUGH_MONEY,
                missing=price - user.money
            )

        new_level = level + 1

        try:
            await self.ghoul_repo.update_kagune_strength(
                telegram_id=user_id,
                new_strength=new_level
            )

            new_balance = await self.family_service.change_wallet(user_id, -price)

            await self.cooldown_service.set(
                telegram_id=user_id,
                action=CooldownAction.KAGUNE_GROW,
                duration=apply_effect(user, EffectKey.KAGUNE_COOLDOWN, game_cfg.kagune.cooldown)
            )
        except Exception:
            kagune_logger.exception(f"[KAGUNE] Upgrade kagune failed | user_id={user_id} | price={price}")
            raise

        ghoul.kagune_strength = new_level
        user.money = new_balance

        kagune_logger.info(
            f"[KAGUNE] Level upgraded | user_id={user_id} | "
            f"old_level={level} | new_level={ghoul.kagune_strength} | price={price}"
        )
        
        text = cfg['message']['kagune']['kagune_up'].format(
                new_lvl=ghoul.kagune_strength,
                price=format_num(price)
            )

        return KaguneResult(
            status=ResultStatus.SUCCESS,
            text=text,
            collection=self.ghoul_service.get_kagune_collection(ghoul.kagune_type)
        )