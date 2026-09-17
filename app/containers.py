from contextvars import ContextVar

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from dependency_injector import providers, containers

from app.database.repositories import (
    ChatRepository,
    GhoulRepository,
    QuizRepository,
    TopsRepository,
    UserCooldownRepository,
    UserRepository,
    LotteryRepository,
    RpCommandRepository,
    TransferRepository,
)

from app.services import (
    BanService,
    ChatService,
    ResetService,
    CooldownService,
    CoffeeService,
    GhoulService,
    KaguneService,
    ModifyBalanceService,
    FieldEditService,
    PlayerLookupService,
    ProfileService,
    QuizService,
    RaceProfileService,
    SnapService,
    StartService,
    StatsService,
    TopsService,
    WordleService,
    LotteryService,
    LotteryVideoGenerator,
    RpCommandService,
    TransferService,
    BroadcastService,
    WikipediaService,
)

session_context: ContextVar[AsyncSession] = ContextVar("session_context")

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    bot = providers.Dependency(instance_of=Bot)

    db_session = providers.Factory(lambda: session_context.get(None))

    # repositories
    user_repo = providers.Factory(UserRepository, session=db_session)
    ghoul_repo = providers.Factory(GhoulRepository, session=db_session)
    user_cooldown_repo = providers.Factory(UserCooldownRepository, session=db_session)
    chat_repo = providers.Factory(ChatRepository, session=db_session)
    quiz_repo = providers.Factory(QuizRepository, session=db_session)
    tops_repo = providers.Factory(TopsRepository, session=db_session)
    lottery_repo = providers.Factory(LotteryRepository, session=db_session)
    rp_repo = providers.Factory(RpCommandRepository, session=db_session)
    transfer_repo = providers.Factory(TransferRepository, session=db_session)

    # services
    ban_service = providers.Factory(BanService, user_repo=user_repo)
    modify_balance_service = providers.Factory(ModifyBalanceService, user_repo=user_repo)
    player_lookup_service = providers.Factory(PlayerLookupService, user_repo=user_repo, ghoul_repo=ghoul_repo)
    field_edit_service = providers.Factory(FieldEditService, user_repo=user_repo, ghoul_repo=ghoul_repo)
    reset_service = providers.Factory(ResetService, user_repo=user_repo, ghoul_repo=ghoul_repo)
    broadcast_service = providers.Factory(BroadcastService, user_repo=user_repo, chat_repo=chat_repo, bot=bot)

    chat_service = providers.Factory(ChatService, chat_repo=chat_repo)

    start_service = providers.Factory(StartService, user_repo=user_repo)
    profile_service = providers.Factory(ProfileService)
    rp_command_service = providers.Factory(RpCommandService, rp_repo=rp_repo)
    transfer_service = providers.Factory(TransferService, transfer_repo=transfer_repo, user_repo=user_repo)

    wordle_service = providers.Singleton(WordleService)
    quiz_service = providers.Factory(QuizService, user_repo=user_repo, quiz_repo=quiz_repo)
    lottery_video_generator = providers.Singleton(LotteryVideoGenerator)
    lottery_service = providers.Factory(
        LotteryService,
        user_repo=user_repo,
        lottery_repo=lottery_repo,
        video_generator=lottery_video_generator
    )

    cooldown_service = providers.Factory(CooldownService, user_cooldown_repo=user_cooldown_repo)

    ghoul_service = providers.Factory(GhoulService, ghoul_repo=ghoul_repo)
    kagune_service = providers.Factory(
        KaguneService,
        ghoul_repo=ghoul_repo,
        user_repo=user_repo,
        cooldown_service=cooldown_service,
        ghoul_service=ghoul_service
    )
    stats_service = providers.Factory(StatsService, ghoul_repo=ghoul_repo, user_repo=user_repo)
    coffee_service = providers.Factory(
        CoffeeService,
        ghoul_repo=ghoul_repo,
        user_repo=user_repo,
        cooldown_service=cooldown_service
    )
    snap_service = providers.Factory(
        SnapService,
        ghoul_repo=ghoul_repo,
        user_repo=user_repo,
        cooldown_service=cooldown_service
    )
    race_profile_service = providers.Factory(RaceProfileService, ghoul_service=ghoul_service)

    tops_service = providers.Factory(TopsService, tops_repo=tops_repo)

    wikipedia_service = providers.Factory(WikipediaService)