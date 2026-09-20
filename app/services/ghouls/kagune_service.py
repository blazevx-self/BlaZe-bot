from app.configs.game import game_cfg
from app.configs.yaml_loader import cfg

from app.core.enums import ResultStatus
from app.core.enums.cooldown_action import CooldownAction
from app.core.exceptions.ghoul import KaguneInitializationError

from app.types.services_result.ghoul import KaguneResult
from app.types.entities.user import UserData
from app.types.entities.ghoul import GhoulData

from app.database.repositories.ghoul_repository import GhoulRepository
from app.database.repositories.user_repository import UserRepository

from app.services.ghouls.ghoul_service import GhoulService
from app.services.cooldown_service import CooldownService

from app.utils.format_num import format_num
from app.utils.logger import kagune_logger

class KaguneService:
    def __init__(
        self,
        ghoul_repo: GhoulRepository,
        user_repo: UserRepository,
        ghoul_service: GhoulService,
        cooldown_service: CooldownService
    ):
        self.ghoul_repo = ghoul_repo
        self.user_repo = user_repo
        self.ghoul_service = ghoul_service
        self.cooldown_service = cooldown_service

    async def obtaining_kagune(self, user: UserData, ghoul: GhoulData | None) -> KaguneResult:
        if ghoul is not None and ghoul.kagune_was_obtained:
            return KaguneResult(status=ResultStatus.ALREADY_GHOUL)

        user_id = user.telegram_id
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

        return KaguneResult(
            status=ResultStatus.SUCCESS,
            kagune_type=kagune_type,
            gif=self.ghoul_service.get_kagune_obtained_gif()
        )

    async def upgrade_kagune(self, user: UserData, ghoul: GhoulData) -> KaguneResult:
        user_id = user.telegram_id

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
        price = self.ghoul_service.get_price_kagune(level)

        # проверка баланса перед апом
        if user.money < price:
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

            new_balance = await self.user_repo.change_money(
                telegram_id=user_id,
                amount=-price
            )

            await self.cooldown_service.set(
                telegram_id=user_id,
                action=CooldownAction.KAGUNE_GROW,
                duration=game_cfg.kagune.cooldown
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
            gif=self.ghoul_service.get_kagune_gif(
                ghoul.kagune_type
            )
        )