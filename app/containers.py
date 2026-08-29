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
)

from app.services import (
    BanService,
    ChatService,
    CooldownService,
    CoffeeService,
    GhoulService,
    KaguneService,
    ModifyBalanceService,
    PlayerLookupService,
    ProfileService,
    QuizService,
    RaceProfileService,
    SnapService,
    StartService,
    StatsService,
    TopsService,
    WordleService,
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

    # services
    ban_service = providers.Factory(BanService, user_repo=user_repo)
    modify_balance_service = providers.Factory(ModifyBalanceService, user_repo=user_repo)
    player_lookup_service = providers.Factory(PlayerLookupService, user_repo=user_repo, ghoul_repo=ghoul_repo)

    chat_service = providers.Factory(ChatService, chat_repo=chat_repo)

    start_service = providers.Factory(StartService, user_repo=user_repo)
    profile_service = providers.Factory(ProfileService)

    wordle_service = providers.Singleton(WordleService)
    quiz_service = providers.Factory(QuizService, user_repo=user_repo, quiz_repo=quiz_repo)

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